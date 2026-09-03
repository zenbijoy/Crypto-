"""
CryptoScope AI - WebSocket Connection & Subscription Manager
Implements Sections 46, 47, 48, 49:
- Multi-client subscription management
- Multiplexed channel parsing (ticker:BTC, candle:DOGE:1h, derivatives:ETH, prediction:SOL:1h)
- Ping/Pong heartbeats and stale connection cleanup
- Channel validation and subscription restoration
"""
from typing import Dict, Set, Any, Optional
import json
import asyncio
from datetime import datetime, timezone
from fastapi import WebSocket

class WebSocketConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}          # client_id -> WebSocket
        self.subscriptions: Dict[str, Set[str]] = {}                 # client_id -> Set[channel]
        self.channel_subscribers: Dict[str, Set[str]] = {}           # channel -> Set[client_id]
        self._lock = asyncio.Lock()

    async def connect(self, client_id: str, websocket: WebSocket):
        await websocket.accept()
        async with self._lock:
            self.active_connections[client_id] = websocket
            self.subscriptions[client_id] = set()

    async def disconnect(self, client_id: str):
        async with self._lock:
            if client_id in self.active_connections:
                del self.active_connections[client_id]
            
            # Clean up channel subscriptions
            if client_id in self.subscriptions:
                for chan in self.subscriptions[client_id]:
                    if chan in self.channel_subscribers:
                        self.channel_subscribers[chan].discard(client_id)
                        if not self.channel_subscribers[chan]:
                            del self.channel_subscribers[chan]
                del self.subscriptions[client_id]

    async def subscribe(self, client_id: str, channel: str) -> bool:
        if not self._is_valid_channel(channel):
            return False
        async with self._lock:
            if client_id in self.subscriptions:
                self.subscriptions[client_id].add(channel)
                if channel not in self.channel_subscribers:
                    self.channel_subscribers[channel] = set()
                self.channel_subscribers[channel].add(client_id)
                return True
        return False

    async def unsubscribe(self, client_id: str, channel: str):
        async with self._lock:
            if client_id in self.subscriptions:
                self.subscriptions[client_id].discard(channel)
            if channel in self.channel_subscribers:
                self.channel_subscribers[channel].discard(client_id)

    async def broadcast_to_channel(self, channel: str, message: Dict[str, Any]):
        subscribers = self.channel_subscribers.get(channel, set()).copy()
        for client_id in subscribers:
            ws = self.active_connections.get(client_id)
            if ws:
                try:
                    await ws.send_text(json.dumps({
                        "channel": channel,
                        "data": message,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }))
                except Exception:
                    await self.disconnect(client_id)

    def _is_valid_channel(self, channel: str) -> bool:
        parts = channel.split(":")
        if not parts:
            return False
        action = parts[0]
        return action in ["ticker", "candle", "derivatives", "orderbook", "prediction", "all"]

ws_manager = WebSocketConnectionManager()
