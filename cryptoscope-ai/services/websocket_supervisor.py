"""
CryptoScope AI - Production Resilient WebSocket Supervisor & Order Book Sync
Implements Step 5 Specifications:
- WebSocket connection lifecycle management with exponential backoff & jitter
- Heartbeat / ping-pong monitoring & stale feed detection
- Subscription restoration upon reconnection
- Strict Order Book synchronization algorithm:
  * Buffer WebSocket depth diff events
  * Fetch REST depth snapshot
  * Drop older events, match first event (U <= lastUpdateId <= u)
  * Verify sequence integrity (each event's pu == previous u)
  * On gap or corruption: mark order book INVALID, suppress dependent features, trigger auto-resnapshot
"""
import asyncio
import json
import logging
import random
import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Callable, Set
import websockets

from core.enums import Provider
from core.models import OrderBookSnapshot, OrderBookDelta
from core.http_client import http_engine
from core.exceptions import ProviderError, DataUnavailableError

logger = logging.getLogger("cryptoscope.ws_supervisor")


class FeedState:
    DISCONNECTED = "DISCONNECTED"
    CONNECTING = "CONNECTING"
    CONNECTED = "CONNECTED"
    RECONNECTING = "RECONNECTING"
    STALE = "STALE"


class OrderBookSyncState:
    INITIALIZING = "INITIALIZING"
    BUFFERING = "BUFFERING"
    SYNCHRONIZED = "SYNCHRONIZED"
    INVALID = "INVALID"


class ManagedOrderBook:
    """
    Maintains a locally synchronized L2 orderbook with Binance sequence validation.
    """
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.state = OrderBookSyncState.INITIALIZING
        self.bids: Dict[float, float] = {}  # price -> qty
        self.asks: Dict[float, float] = {}  # price -> qty
        self.last_update_id: int = 0
        self.event_buffer: List[Dict[str, Any]] = []
        self.last_sync_time: Optional[datetime] = None
        self.sequence_gap_count: int = 0

    def reset(self):
        self.state = OrderBookSyncState.INITIALIZING
        self.bids.clear()
        self.asks.clear()
        self.last_update_id = 0
        self.event_buffer.clear()

    def buffer_depth_event(self, event: Dict[str, Any]):
        """Buffers depthUpdate events while waiting for or applying REST snapshot."""
        if self.state == OrderBookSyncState.BUFFERING:
            self.event_buffer.append(event)
        elif self.state == OrderBookSyncState.SYNCHRONIZED:
            self.apply_delta_event(event)

    def apply_snapshot(self, snapshot_data: Dict[str, Any]):
        """
        Applies REST snapshot and replays buffered events to establish synchronized state.
        """
        self.last_update_id = int(snapshot_data["lastUpdateId"])
        self.bids = {float(p): float(q) for p, q in snapshot_data["bids"]}
        self.asks = {float(p): float(q) for p, q in snapshot_data["asks"]}
        self.last_sync_time = datetime.now(timezone.utc)

        # Replay buffered events
        valid_events = []
        for ev in self.event_buffer:
            u = int(ev["u"])
            U = int(ev["U"])
            # In Binance futures: drop event if u < lastUpdateId
            if u < self.last_update_id:
                continue
            # First event must satisfy: U <= lastUpdateId and u >= lastUpdateId
            if not valid_events:
                if U <= self.last_update_id <= u:
                    valid_events.append(ev)
                continue
            valid_events.append(ev)

        self.event_buffer.clear()
        self.state = OrderBookSyncState.SYNCHRONIZED

        for ev in valid_events:
            self.apply_delta_event(ev)

        logger.info("Order book %s successfully synchronized at update_id=%d", self.symbol, self.last_update_id)

    def apply_delta_event(self, event: Dict[str, Any]):
        """
        Validates sequence integrity and updates price levels.
        If sequence gap detected, marks book INVALID.
        """
        U = int(event["U"])
        u = int(event["u"])
        pu = int(event.get("pu", -1))

        # Check sequence continuity in Binance USD-M futures: pu should equal previous u
        if pu != -1 and pu != self.last_update_id:
            logger.warning(
                "Sequence gap detected for %s: event.pu=%d != book.last_update_id=%d. Invalidating book!",
                self.symbol, pu, self.last_update_id
            )
            self.state = OrderBookSyncState.INVALID
            self.sequence_gap_count += 1
            return

        # Update bids
        for p_str, q_str in event.get("b", []):
            p = float(p_str)
            q = float(q_str)
            if q == 0.0:
                self.bids.pop(p, None)
            else:
                self.bids[p] = q

        # Update asks
        for p_str, q_str in event.get("a", []):
            p = float(p_str)
            q = float(q_str)
            if q == 0.0:
                self.asks.pop(p, None)
            else:
                self.asks[p] = q

        self.last_update_id = u
        self.last_sync_time = datetime.now(timezone.utc)

    def get_snapshot(self, depth: int = 50) -> Optional[OrderBookSnapshot]:
        """Returns sorted canonical L2 snapshot if book is valid and synchronized."""
        if self.state != OrderBookSyncState.SYNCHRONIZED or not self.bids or not self.asks:
            return None

        sorted_bids = sorted(self.bids.items(), key=lambda x: x[0], reverse=True)[:depth]
        sorted_asks = sorted(self.asks.items(), key=lambda x: x[0])[:depth]

        if not sorted_bids or not sorted_asks:
            return None

        best_bid = sorted_bids[0][0]
        best_ask = sorted_asks[0][0]
        if best_bid >= best_ask:
            logger.error("Book crossed for %s: best_bid=%.2f >= best_ask=%.2f", self.symbol, best_bid, best_ask)
            self.state = OrderBookSyncState.INVALID
            return None

        mid_price = (best_bid + best_ask) / 2.0
        spread_bps = ((best_ask - best_bid) / mid_price) * 10000.0

        bid_vol = sorted_bids[0][1]
        ask_vol = sorted_asks[0][1]
        microprice = ((best_bid * ask_vol) + (best_ask * bid_vol)) / (bid_vol + ask_vol) if (bid_vol + ask_vol) > 0 else mid_price

        band_10bps = mid_price * 0.0010
        bid_depth_10bps = sum(q for p, q in sorted_bids if p >= (mid_price - band_10bps))
        ask_depth_10bps = sum(q for p, q in sorted_asks if p <= (mid_price + band_10bps))
        tot_10bps = bid_depth_10bps + ask_depth_10bps
        imbalance_10bps = ((bid_depth_10bps - ask_depth_10bps) / tot_10bps) if tot_10bps > 0 else 0.0

        band_5bps = mid_price * 0.0005
        depth_5bps_usd = sum(p * q for p, q in sorted_bids if p >= (mid_price - band_5bps)) + \
                         sum(p * q for p, q in sorted_asks if p <= (mid_price + band_5bps))

        depth_10bps_usd = sum(p * q for p, q in sorted_bids if p >= (mid_price - band_10bps)) + \
                          sum(p * q for p, q in sorted_asks if p <= (mid_price + band_10bps))

        now_utc = datetime.now(timezone.utc)
        return OrderBookSnapshot(
            provider=Provider.BINANCE,
            symbol=self.symbol,
            event_time=self.last_sync_time or now_utc,
            available_time=now_utc,
            ingested_at=now_utc,
            last_update_id=self.last_update_id,
            bids=[[p, q] for p, q in sorted_bids],
            asks=[[p, q] for p, q in sorted_asks],
            spread_bps=round(spread_bps, 2),
            mid_price=round(mid_price, 4),
            microprice=round(microprice, 4),
            imbalance_10bps=round(imbalance_10bps, 4),
            depth_5bps_usd=round(depth_5bps_usd, 2),
            depth_10bps_usd=round(depth_10bps_usd, 2)
        )


class WebSocketSupervisor:
    """
    Supervises the Binance USD-M WebSocket connection stream.
    Handles automatic reconnection, heartbeats, staleness checks, and orderbook synchronization.
    """
    def __init__(
        self,
        base_ws_url: str = "wss://fstream.binance.com/ws",
        stale_threshold_seconds: float = 15.0
    ):
        self.base_ws_url = base_ws_url
        self.stale_threshold_seconds = stale_threshold_seconds
        self.state = FeedState.DISCONNECTED
        self.subscriptions: Set[str] = set()
        self.orderbooks: Dict[str, ManagedOrderBook] = {}
        
        # Telemetry & Metrics
        self.messages_received: int = 0
        self.reconnect_count: int = 0
        self.last_message_time: float = 0.0
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._ws: Optional[websockets.WebSocketClientProtocol] = None
        self._callbacks: List[Callable[[Dict[str, Any]], None]] = []

    def register_callback(self, cb: Callable[[Dict[str, Any]], None]):
        self._callbacks.append(cb)

    def subscribe(self, stream_name: str):
        self.subscriptions.add(stream_name.lower())

    def get_or_create_orderbook(self, symbol: str) -> ManagedOrderBook:
        clean_sym = symbol.upper()
        if clean_sym not in self.orderbooks:
            self.orderbooks[clean_sym] = ManagedOrderBook(clean_sym)
        return self.orderbooks[clean_sym]

    async def synchronize_orderbook(self, symbol: str):
        """
        Executes the official Binance depth synchronization flow:
        1. Set state to BUFFERING
        2. Request REST depth snapshot
        3. Apply snapshot and replay buffered diff events
        """
        book = self.get_or_create_orderbook(symbol)
        book.state = OrderBookSyncState.BUFFERING
        
        # Subscribe to diff stream: <symbol>@depth@100ms
        stream = f"{symbol.lower()}@depth@100ms"
        self.subscribe(stream)

        # Fetch REST snapshot
        try:
            url = f"https://fapi.binance.com/fapi/v1/depth?symbol={symbol.upper()}&limit=1000"
            snapshot_data, _ = await http_engine.request("GET", url, max_retries=3)
            book.apply_snapshot(snapshot_data)
        except Exception as exc:
            logger.error("Failed to fetch REST orderbook snapshot for %s: %s", symbol, exc)
            book.state = OrderBookSyncState.INVALID

    async def start(self):
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info("WebSocket Supervisor started.")

    async def stop(self):
        self._running = False
        if self._ws:
            await self._ws.close()
        if self._task:
            self._task.cancel()
        self.state = FeedState.DISCONNECTED
        logger.info("WebSocket Supervisor stopped.")

    async def _run_loop(self):
        attempt = 0
        while self._running:
            self.state = FeedState.CONNECTING
            try:
                # Binance combined stream URL if subscriptions exist
                if self.subscriptions:
                    streams_path = "/".join(sorted(self.subscriptions))
                    url = f"wss://fstream.binance.com/stream?streams={streams_path}"
                else:
                    url = f"{self.base_ws_url}/!markPrice@arr@1s"

                logger.info("Connecting to WebSocket: %s", url)
                async with websockets.connect(
                    url,
                    ping_interval=20,
                    ping_timeout=10,
                    close_timeout=5
                ) as ws:
                    self._ws = ws
                    self.state = FeedState.CONNECTED
                    self.last_message_time = time.monotonic()
                    attempt = 0
                    logger.info("WebSocket connected successfully.")

                    while self._running:
                        try:
                            msg = await asyncio.wait_for(ws.recv(), timeout=self.stale_threshold_seconds)
                            self.messages_received += 1
                            self.last_message_time = time.monotonic()
                            data = json.loads(msg)
                            self._handle_message(data)
                        except asyncio.TimeoutError:
                            logger.warning("WebSocket feed became STALE (no message in %.1fs). Reconnecting.", self.stale_threshold_seconds)
                            self.state = FeedState.STALE
                            break

            except (websockets.ConnectionClosed, Exception) as exc:
                self.reconnect_count += 1
                self.state = FeedState.RECONNECTING
                attempt += 1
                backoff = min(30.0, random.uniform(1.0, 2.0 ** min(attempt, 5)))
                logger.warning("WebSocket disconnected (%s). Reconnecting in %.1fs (attempt %d)", str(exc), backoff, attempt)
                await asyncio.sleep(backoff)

    def _handle_message(self, data: Dict[str, Any]):
        """Routes stream messages to callbacks and orderbooks."""
        payload = data.get("data", data)
        event_type = payload.get("e")

        if event_type == "depthUpdate":
            sym = payload.get("s", "").upper()
            if sym in self.orderbooks:
                book = self.orderbooks[sym]
                book.buffer_depth_event(payload)
                if book.state == OrderBookSyncState.INVALID:
                    # Trigger async resnapshot
                    asyncio.create_task(self.synchronize_orderbook(sym))

        for cb in self._callbacks:
            try:
                cb(payload)
            except Exception as e:
                logger.error("Error in WS callback: %s", e)


# Global WebSocket supervisor singleton
ws_supervisor = WebSocketSupervisor()
