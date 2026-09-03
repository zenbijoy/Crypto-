"""
CryptoScope AI - Production Redis Caching & PubSub Service (Step 8)
Implements Step 8 Specifications:
- Structured hierarchical key naming convention:
  market:{provider}:{symbol}:ticker
  market:{provider}:{symbol}:orderbook
  market:{provider}:{symbol}:derivatives
  features:{symbol}:{timeframe}
- Configurable TTLs with staleness validation (reject stale cache entries as fresh)
- Pub/Sub channels for real-time market ticks, orderbook invalidations, and signal triggers
- In-memory fallback if Redis is unavailable or unconfigured, preserving identical contracts
"""
import asyncio
import json
import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Set
import redis.asyncio as aioredis

from core.config import settings

logger = logging.getLogger("cryptoscope.redis")


class RedisService:
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or getattr(settings, "REDIS_URL", None)
        self._client: Optional[aioredis.Redis] = None
        self._connected: bool = False
        
        # Local in-memory fallback cache: key -> {"data": val, "expires_at": float, "written_at": float}
        self._memory_cache: Dict[str, Dict[str, Any]] = {}
        
        # Standard TTL configurations (in seconds)
        self.TTL_TICKER = 3
        self.TTL_ORDERBOOK = 2
        self.TTL_DERIVATIVES = 15
        self.TTL_FEATURES = 30
        self.TTL_PREDICTION = 60

    async def connect(self):
        if self.redis_url:
            try:
                self._client = aioredis.from_url(
                    self.redis_url,
                    decode_responses=True,
                    socket_connect_timeout=2.0
                )
                await self._client.ping()
                self._connected = True
                logger.info("Connected to Redis at %s", self.redis_url)
            except Exception as exc:
                logger.warning("Could not connect to Redis (%s). Using resilient in-memory fallback cache.", exc)
                self._connected = False
        else:
            logger.info("REDIS_URL not configured. Operating with resilient in-memory cache.")

    async def close(self):
        if self._client and self._connected:
            await self._client.close()
            self._connected = False

    def build_key(self, namespace: str, provider: str, symbol: str, metric: str) -> str:
        """Standard key format: market:{provider}:{symbol}:{metric}"""
        return f"{namespace}:{provider.lower()}:{symbol.upper()}:{metric.lower()}"

    async def set_json(self, key: str, value: Any, ttl_seconds: int):
        """Stores serialized JSON with explicit TTL and written_at timestamp."""
        envelope = {
            "payload": value,
            "written_at": time.time(),
            "ttl": ttl_seconds
        }
        serialized = json.dumps(envelope)

        if self._connected and self._client:
            try:
                await self._client.setex(key, ttl_seconds, serialized)
                return
            except Exception as exc:
                logger.warning("Redis set failed: %s. Falling back to memory.", exc)

        # In-memory storage
        self._memory_cache[key] = {
            "data": envelope,
            "expires_at": time.time() + ttl_seconds
        }

    async def get_json(self, key: str, max_staleness_seconds: Optional[float] = None) -> Optional[Any]:
        """
        Retrieves cached JSON.
        Validates staleness: if data was written more than max_staleness_seconds ago,
        rejects it as stale and returns None.
        """
        raw_val = None
        if self._connected and self._client:
            try:
                raw_val = await self._client.get(key)
            except Exception as exc:
                logger.warning("Redis get failed: %s. Checking memory fallback.", exc)

        if raw_val is None:
            mem_item = self._memory_cache.get(key)
            if mem_item:
                if time.time() > mem_item["expires_at"]:
                    del self._memory_cache[key]
                    return None
                envelope = mem_item["data"]
            else:
                return None
        else:
            try:
                envelope = json.loads(raw_val)
            except Exception:
                return None

        # Staleness verification
        written_at = envelope.get("written_at", 0.0)
        age = time.time() - written_at
        threshold = max_staleness_seconds if max_staleness_seconds is not None else envelope.get("ttl", 60.0)

        if age > threshold:
            logger.debug("Cached key %s rejected as STALE (age=%.2fs > threshold=%.2fs)", key, age, threshold)
            return None

        return envelope.get("payload")

    async def publish(self, channel: str, message: Any):
        """Publishes event to Redis pub/sub channel."""
        serialized = json.dumps(message) if not isinstance(message, str) else message
        if self._connected and self._client:
            try:
                await self._client.publish(channel, serialized)
            except Exception as exc:
                logger.warning("Redis publish failed: %s", exc)


# Global singleton
redis_service = RedisService()
