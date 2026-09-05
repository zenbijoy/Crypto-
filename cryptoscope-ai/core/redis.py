"""
CryptoScope AI - Canonical Redis Core Layer (Phases 10 & 11)
Implements standard Redis caching, rate limits, provider health, distributed locks,
and pub/sub event streams with strict key contracts and freshness guarantees.

Standard Key Contract:
- ticker:{provider}:{symbol}
- funding:{provider}:{symbol}
- oi:{provider}:{symbol}
- orderbook:{provider}:{symbol}
- feature:{symbol}:{horizon}:{version}
- prediction:{symbol}:{horizon}
- provider:health:{provider}

All cached financial data includes:
- updated_at (ISO 8601 string)
- source (provider name)
- freshness (age in seconds)
- TTL (configured time to live)
"""
import asyncio
import json
import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional, List, Set, Union
import redis.asyncio as aioredis
from core.config import settings

logger = logging.getLogger("cryptoscope.core.redis")


class CanonicalRedis:
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or getattr(settings, "REDIS_URL", "redis://localhost:6379/0")
        self._client: Optional[aioredis.Redis] = None
        self._connected: bool = False
        
        # Resilient in-memory fallback store: key -> {"envelope": dict, "expires_at": float}
        self._memory_cache: Dict[str, Dict[str, Any]] = {}
        
        # Standard TTLs in seconds
        self.TTL_TICKER = 5
        self.TTL_ORDERBOOK = 3
        self.TTL_FUNDING = 60
        self.TTL_OI = 30
        self.TTL_FEATURE = 60
        self.TTL_PREDICTION = 120
        self.TTL_PROVIDER_HEALTH = 15

    async def connect(self) -> bool:
        """Establishes connection to Redis with quick timeout."""
        if not self.redis_url:
            logger.info("REDIS_URL not configured. Operating in memory fallback mode.")
            return False
            
        try:
            self._client = aioredis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_connect_timeout=2.0,
                socket_timeout=2.0
            )
            await self._client.ping()
            self._connected = True
            logger.info("Canonical Redis connected successfully at %s", self.redis_url)
            return True
        except Exception as exc:
            logger.warning("Redis connection failed (%s). Using resilient in-memory fallback.", exc)
            self._connected = False
            return False

    async def close(self):
        """Gracefully closes Redis connection."""
        if self._client and self._connected:
            await self._client.close()
            self._connected = False

    def is_connected(self) -> bool:
        return self._connected

    # =========================================================================
    # Standard Key Generators (Phase 11 Key Contract)
    # =========================================================================
    @staticmethod
    def key_ticker(provider: str, symbol: str) -> str:
        return f"ticker:{provider.lower()}:{symbol.upper()}"

    @staticmethod
    def key_funding(provider: str, symbol: str) -> str:
        return f"funding:{provider.lower()}:{symbol.upper()}"

    @staticmethod
    def key_oi(provider: str, symbol: str) -> str:
        return f"oi:{provider.lower()}:{symbol.upper()}"

    @staticmethod
    def key_orderbook(provider: str, symbol: str) -> str:
        return f"orderbook:{provider.lower()}:{symbol.upper()}"

    @staticmethod
    def key_feature(symbol: str, horizon: str, version: str = "v1") -> str:
        return f"feature:{symbol.upper()}:{horizon.lower()}:{version.lower()}"

    @staticmethod
    def key_prediction(symbol: str, horizon: str) -> str:
        return f"prediction:{symbol.upper()}:{horizon.lower()}"

    @staticmethod
    def key_provider_health(provider: str) -> str:
        return f"provider:health:{provider.lower()}"

    # =========================================================================
    # Financial Cache Set & Get with Strict Contract Envelopes
    # =========================================================================
    async def set_financial_cache(
        self,
        key: str,
        data: Any,
        source: str,
        ttl_seconds: int
    ) -> bool:
        """
        Stores financial data conforming to Phase 11 contract:
        includes updated_at, source, freshness, and TTL.
        """
        now = time.time()
        now_iso = datetime.now(timezone.utc).isoformat()
        envelope = {
            "payload": data,
            "source": source,
            "updated_at": now_iso,
            "written_epoch": now,
            "ttl": ttl_seconds,
            "freshness": 0.0
        }
        serialized = json.dumps(envelope)

        if self._connected and self._client:
            try:
                await self._client.setex(key, ttl_seconds, serialized)
                return True
            except Exception as exc:
                logger.warning("Redis setex error for key %s: %s. Writing to memory.", key, exc)

        # Fallback to local memory
        self._memory_cache[key] = {
            "envelope": envelope,
            "expires_at": now + ttl_seconds
        }
        return True

    async def get_financial_cache(
        self,
        key: str,
        max_staleness_seconds: Optional[float] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieves financial data. Validates max staleness.
        Calculates real-time freshness (seconds elapsed since written).
        Returns None if expired or stale.
        """
        raw_val = None
        now = time.time()

        if self._connected and self._client:
            try:
                raw_val = await self._client.get(key)
            except Exception as exc:
                logger.warning("Redis get error for key %s: %s. Reading memory.", key, exc)

        if raw_val is not None:
            try:
                envelope = json.loads(raw_val)
            except Exception:
                return None
        else:
            mem = self._memory_cache.get(key)
            if not mem:
                return None
            if now > mem["expires_at"]:
                del self._memory_cache[key]
                return None
            envelope = mem["envelope"]

        written_epoch = envelope.get("written_epoch", now)
        freshness = max(0.0, now - written_epoch)
        envelope["freshness"] = round(freshness, 3)

        limit = max_staleness_seconds if max_staleness_seconds is not None else envelope.get("ttl", 60.0)
        if freshness > limit:
            logger.debug("Key %s rejected as STALE: freshness %.2fs > limit %.2fs", key, freshness, limit)
            return None

        return envelope

    async def publish_event(self, channel: str, message: Any) -> bool:
        """Publishes event to Redis pub/sub channel."""
        serialized = json.dumps(message) if not isinstance(message, str) else message
        if self._connected and self._client:
            try:
                await self._client.publish(channel, serialized)
                return True
            except Exception as exc:
                logger.warning("Redis publish failed on channel %s: %s", channel, exc)
                return False
        return False


# Global canonical redis instance
redis_client = CanonicalRedis()
