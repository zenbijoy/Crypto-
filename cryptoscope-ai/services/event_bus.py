"""
Production Event Bus for CryptoScope AI using Redis Streams.
Phase 3: Event Bus Architecture.
"""
from __future__ import annotations
import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Set
import redis.asyncio as aioredis

from core.events import CanonicalEvent, EventType
from services.dlq import dlq_manager

logger = logging.getLogger("CryptoScope.EventBus")

STREAMS = [
    "market:trades",
    "market:candles",
    "market:orderbook",
    "market:funding",
    "market:oi",
    "market:liquidations",
    "features:realtime",
    "predictions",
    "signals",
    "paper:orders",
    "system:events",
]


class EventBus:
    """Production asynchronous Event Bus backed by Redis Streams with in-process resilient fallback."""

    def __init__(self, redis_url: str = "redis://localhost:6379", max_stream_length: int = 50000):
        self.redis_url = redis_url
        self.max_stream_length = max_stream_length
        self._redis: Optional[aioredis.Redis] = None
        self._is_connected: bool = False
        self._processed_event_ids: Set[str] = set()
        self._max_id_history = 100000
        # In-memory stream buffer fallback if Redis server is offline
        self._local_streams: Dict[str, List[Dict[str, Any]]] = {s: [] for s in STREAMS}
        self._local_consumers: Dict[str, Dict[str, int]] = {}  # stream -> {group: offset}
        self._stream_stats: Dict[str, Dict[str, int]] = {
            s: {"published": 0, "consumed": 0, "lag": 0, "dropped": 0} for s in STREAMS
        }

    async def initialize(self) -> bool:
        """Connect to Redis or initialize resilient stream fallback."""
        try:
            client = aioredis.from_url(self.redis_url, decode_responses=True, socket_timeout=1.0)
            await client.ping()
            self._redis = client
            self._is_connected = True
            logger.info(f"[EventBus] Connected to live Redis Streams at {self.redis_url}")
            await self._ensure_stream_groups()
            return True
        except Exception as e:
            logger.warning(f"[EventBus] Live Redis unavailable ({e}). Initializing resilient in-process Stream Bus.")
            try:
                import fakeredis.aioredis as fake_aioredis
                self._redis = fake_aioredis.FakeRedis(decode_responses=True)
                self._is_connected = True
                await self._ensure_stream_groups()
                logger.info("[EventBus] Successfully initialized high-fidelity in-process Stream Bus.")
                return True
            except Exception as fe:
                logger.error(f"[EventBus] In-process stream initialization failed: {fe}")
                self._is_connected = False
                return False

    async def _ensure_stream_groups(self):
        if not self._redis:
            return
        for s in STREAMS:
            try:
                await self._redis.xgroup_create(s, "default_group", id="0", mkstream=True)
            except Exception:
                pass  # Group already exists

    async def publish(self, stream: str, event: CanonicalEvent) -> str:
        """Publish canonical event with idempotency check, backpressure protection, and DLQ routing."""
        # 1. Idempotency check
        if event.event_id in self._processed_event_ids:
            logger.debug(f"[EventBus] Dropping duplicate event {event.event_id} on stream {stream}")
            return event.event_id

        # Maintain bounded ID history
        if len(self._processed_event_ids) >= self._max_id_history:
            self._processed_event_ids.clear()
        self._processed_event_ids.add(event.event_id)

        # 2. Update stats
        if stream not in self._stream_stats:
            self._stream_stats[stream] = {"published": 0, "consumed": 0, "lag": 0, "dropped": 0}
        self._stream_stats[stream]["published"] += 1

        payload_json = event.to_json()

        # 3. Publish to Redis Stream or local fallback
        if self._redis:
            try:
                msg_id = await self._redis.xadd(
                    name=stream,
                    fields={"data": payload_json, "trace_id": event.trace_id, "event_id": event.event_id},
                    maxlen=self.max_stream_length,
                    approximate=True
                )
                return msg_id
            except Exception as e:
                logger.error(f"[EventBus] Error publishing to Redis stream {stream}: {e}")
                dlq_manager.capture_failure(
                    stream_name=stream,
                    consumer="publisher",
                    original_payload=event.to_dict(),
                    error=e,
                    trace_id=event.trace_id
                )

        # Local resilient fallback
        if stream not in self._local_streams:
            self._local_streams[stream] = []
        if len(self._local_streams[stream]) >= self.max_stream_length:
            self._local_streams[stream].pop(0)
            self._stream_stats[stream]["dropped"] += 1

        local_id = f"{int(datetime.now(timezone.utc).timestamp()*1000)}-0"
        self._local_streams[stream].append({
            "id": local_id,
            "data": payload_json,
            "trace_id": event.trace_id,
            "event_id": event.event_id
        })
        return local_id

    async def consume_group(
        self,
        stream: str,
        group: str,
        consumer: str,
        count: int = 10,
        block_ms: int = 100
    ) -> List[Dict[str, Any]]:
        """Consume messages from a consumer group with auto-recovery and lag accounting."""
        messages = []
        if self._redis:
            try:
                # Ensure group exists
                try:
                    await self._redis.xgroup_create(stream, group, id="0", mkstream=True)
                except Exception:
                    pass

                entries = await self._redis.xreadgroup(
                    groupname=group,
                    consumername=consumer,
                    streams={stream: ">"},
                    count=count,
                    block=block_ms
                )
                if entries:
                    for s_name, msg_list in entries:
                        for msg_id, raw_fields in msg_list:
                            try:
                                event = CanonicalEvent.from_dict(json.loads(raw_fields["data"]))
                                messages.append({"id": msg_id, "event": event, "stream": s_name})
                                if s_name in self._stream_stats:
                                    self._stream_stats[s_name]["consumed"] += 1
                            except Exception as pe:
                                dlq_manager.capture_failure(
                                    stream_name=s_name,
                                    consumer=consumer,
                                    original_payload=raw_fields,
                                    error=pe,
                                    trace_id=raw_fields.get("trace_id", "unknown")
                                )
                return messages
            except Exception as e:
                logger.error(f"[EventBus] consume_group Redis error on {stream}: {e}")

        # Local fallback simulation
        if stream in self._local_streams:
            if stream not in self._local_consumers:
                self._local_consumers[stream] = {}
            offset = self._local_consumers[stream].get(group, 0)
            all_msgs = self._local_streams[stream]
            available = all_msgs[offset:offset + count]
            for item in available:
                try:
                    event = CanonicalEvent.from_dict(json.loads(item["data"]))
                    messages.append({"id": item["id"], "event": event, "stream": stream})
                except Exception as pe:
                    dlq_manager.capture_failure(stream, consumer, item, pe, item.get("trace_id", "unknown"))
            self._local_consumers[stream][group] = offset + len(available)
            if stream in self._stream_stats:
                self._stream_stats[stream]["consumed"] += len(available)

        return messages

    async def acknowledge(self, stream: str, group: str, message_ids: List[str]) -> int:
        """Acknowledge processed message IDs."""
        if not message_ids:
            return 0
        if self._redis:
            try:
                return await self._redis.xack(stream, group, *message_ids)
            except Exception as e:
                logger.error(f"[EventBus] Failed to acknowledge messages in {stream}: {e}")
                return 0
        return len(message_ids)

    async def get_stream_lag(self, stream: str, group: str = "default_group") -> Dict[str, Any]:
        """Measure consumer stream lag."""
        if self._redis:
            try:
                info = await self._redis.xinfo_groups(stream)
                for g in info:
                    if g.get("name") == group:
                        lag = g.get("lag", 0)
                        pending = g.get("pending", 0)
                        return {"stream": stream, "group": group, "lag": lag, "pending": pending}
            except Exception:
                pass

        # Fallback calculation
        stats = self._stream_stats.get(stream, {"published": 0, "consumed": 0})
        lag = max(0, stats["published"] - stats["consumed"])
        return {"stream": stream, "group": group, "lag": lag, "pending": 0}

    async def get_all_stream_metrics(self) -> Dict[str, Any]:
        """Aggregate lag and throughput metrics across all registered streams."""
        metrics = {}
        for s in STREAMS:
            lag_info = await self.get_stream_lag(s)
            stats = self._stream_stats.get(s, {"published": 0, "consumed": 0, "dropped": 0})
            metrics[s] = {
                "published": stats["published"],
                "consumed": stats["consumed"],
                "dropped": stats.get("dropped", 0),
                "lag": lag_info.get("lag", 0)
            }
        return metrics

    async def close(self):
        if self._redis:
            try:
                await self._redis.close()
            except Exception:
                pass


event_bus = EventBus()
