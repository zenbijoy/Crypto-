"""
CryptoScope AI - Upstream Binance USD-M WebSocket Client
Maintains persistent upstream connection to Binance Futures public stream multiplexer:
- wss://fstream.binance.com/stream?streams=...
- Auto-reconnection with bounded exponential backoff & full jitter
- Subscription restoration on reconnect
- Message dispatching, UTC normalization, and zero synthetic ticks on disconnect
"""
import asyncio
import json
import logging
import random
import time
from datetime import datetime, timezone
from typing import Callable, Dict, Any, Optional, List
import websockets

from services.market_stream.subscriptions import stream_registry, StreamType
from services.market_stream.stale_detector import StaleDetector

logger = logging.getLogger("cryptoscope.market_stream.binance")


class BinanceFuturesStreamClient:
    """Upstream client connecting directly to Binance USD-M Futures WebSocket multiplexer."""
    def __init__(
        self,
        base_ws_url: str = "wss://fstream.binance.com/stream",
        stale_threshold_seconds: float = 12.0
    ):
        self.base_ws_url = base_ws_url
        self.stale_detector = StaleDetector(stale_threshold_seconds)
        self._running = False
        self._ws: Optional[websockets.WebSocketClientProtocol] = None
        self._handlers: List[Callable[[Dict[str, Any]], Any]] = []
        self._reconnect_attempts = 0
        self.is_connected = False
        self.last_connected_at: Optional[datetime] = None
        self.total_messages_received: int = 0
        self.error_count: int = 0

    def register_handler(self, handler: Callable[[Dict[str, Any]], Any]):
        self._handlers.append(handler)

    async def start(self):
        """Starts the persistent background connection loop."""
        self._running = True
        stream_registry.setup_default_tier1_streams()
        asyncio.create_task(self._run_loop())

    async def stop(self):
        """Gracefully shuts down the upstream WebSocket."""
        self._running = False
        self.is_connected = False
        if self._ws:
            await self._ws.close()
            self._ws = None
        logger.info("BinanceFuturesStreamClient cleanly stopped.")

    async def _run_loop(self):
        while self._running:
            streams = stream_registry.get_all_streams()
            if not streams:
                await asyncio.sleep(2.0)
                continue

            stream_param = "/".join(streams)
            url = f"{self.base_ws_url}?streams={stream_param}"

            try:
                logger.info("Connecting to Binance upstream WebSocket: %d streams", len(streams))
                async with websockets.connect(
                    url,
                    ping_interval=20,
                    ping_timeout=10,
                    close_timeout=5,
                    max_size=10_000_000
                ) as ws:
                    self._ws = ws
                    self.is_connected = True
                    self.last_connected_at = datetime.now(timezone.utc)
                    self._reconnect_attempts = 0
                    logger.info("Connected to Binance USD-M WebSocket stream.")

                    while self._running:
                        msg = await ws.recv()
                        self.total_messages_received += 1
                        try:
                            payload = json.loads(msg)
                            stream_name = payload.get("stream", "")
                            self.stale_detector.record_event(stream_name)

                            # Dispatch to handlers
                            for handler in self._handlers:
                                if asyncio.iscoroutinefunction(handler):
                                    asyncio.create_task(handler(payload))
                                else:
                                    handler(payload)

                        except json.JSONDecodeError:
                            continue

            except (websockets.ConnectionClosed, websockets.WebSocketException, OSError) as exc:
                self.is_connected = False
                self.error_count += 1
                if not self._running:
                    break

                self._reconnect_attempts += 1
                backoff = min(30.0, random.uniform(1.0, 2.0 ** min(self._reconnect_attempts, 5)))
                logger.warning(
                    "Binance WebSocket disconnected (%s). Reconnecting in %.2fs (attempt %d)",
                    str(exc), backoff, self._reconnect_attempts
                )
                await asyncio.sleep(backoff)
            except Exception as exc:
                self.is_connected = False
                self.error_count += 1
                logger.error("Unexpected Binance WebSocket loop error: %s", exc)
                await asyncio.sleep(3.0)

binance_ws_client = BinanceFuturesStreamClient()
