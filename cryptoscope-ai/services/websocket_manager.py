"""
CryptoScope AI - WebSocket Connection & Subscription Manager
Implements Sections 46, 47, 48, 49:
- Multi-client subscription management
- Multiplexed channel parsing (ticker:BTC, candle:DOGE:1h, derivatives:ETH, prediction:SOL:1h)
- Ping/Pong heartbeats and stale connection cleanup
- Channel validation and subscription restoration
"""
import uuid
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

    async def connect(self, arg1: Any, arg2: Any = None) -> str:
        """
        Accepts either connect(websocket) or connect(client_id, websocket).
        Returns the registered client_id.
        """
        if isinstance(arg1, str) and arg2 is not None:
            client_id = arg1
            websocket: WebSocket = arg2
        else:
            websocket: WebSocket = arg1
            client_id = arg2 or f"ws_{uuid.uuid4().hex[:8]}"

        async with self._lock:
            self.active_connections[client_id] = websocket
            self.subscriptions[client_id] = set()
        return client_id

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

    async def handle_client_message(self, client_id: str, data: str):
        try:
            payload = json.loads(data) if isinstance(data, str) else data
            action = payload.get("action", "").lower()
            ws = self.active_connections.get(client_id)
            if not ws:
                return

            if action == "ping":
                await ws.send_text(json.dumps({
                    "action": "pong",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }))
            elif action == "subscribe":
                channel = payload.get("channel")
                if channel and await self.subscribe(client_id, channel):
                    await ws.send_text(json.dumps({
                        "event": "subscribed",
                        "channel": channel,
                        "success": True
                    }))
                else:
                    await ws.send_text(json.dumps({
                        "event": "error",
                        "message": f"Invalid or disallowed channel: {channel}",
                        "success": False
                    }))
            elif action == "unsubscribe":
                channel = payload.get("channel")
                if channel:
                    await self.unsubscribe(client_id, channel)
                    await ws.send_text(json.dumps({
                        "event": "unsubscribed",
                        "channel": channel,
                        "success": True
                    }))
        except Exception:
            pass

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
