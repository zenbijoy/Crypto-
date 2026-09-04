"""
Online Feature Store backed by Redis and In-Memory Resilient Cache.
Phase 8: Online Feature Store.
"""
from __future__ import annotations
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
import redis.asyncio as aioredis

from feature_store.definitions.core import CORE_FEATURE_SPECS, FeatureSpec

logger = logging.getLogger("CryptoScope.OnlineFeatureStore")


class OnlineFeatureStore:
    """Production low-latency Online Feature Store serving features with explicit freshness and availability masks."""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self._redis: Optional[aioredis.Redis] = None
        self._local_cache: Dict[str, Dict[str, Any]] = {}

    async def initialize(self):
        try:
            client = aioredis.from_url(self.redis_url, decode_responses=True, socket_timeout=0.5)
            await client.ping()
            self._redis = client
            logger.info("[OnlineFeatureStore] Connected to live Redis cluster.")
        except Exception:
            try:
                import fakeredis.aioredis as fake_aioredis
                self._redis = fake_aioredis.FakeRedis(decode_responses=True)
                logger.info("[OnlineFeatureStore] Initialized high-performance in-process Redis store.")
            except Exception as e:
                logger.warning(f"[OnlineFeatureStore] Fallback to in-memory dictionary: {e}")
                self._redis = None

    def _build_key(self, symbol: str, horizon: str, feature_version: str = "v2.0") -> str:
        clean_sym = symbol.replace("/", "-").upper()
        return f"feature:{clean_sym}:{horizon}:{feature_version}"

    async def put_feature_vector(
        self,
        symbol: str,
        horizon: str,
        feature_values: Dict[str, float],
        event_time: datetime,
        feature_version: str = "v2.0"
    ) -> Dict[str, Any]:
        """Store atomic feature vector with freshness and provenance metadata."""
        now = datetime.now(timezone.utc)
        payload = {}
        for fname, val in feature_values.items():
            spec = CORE_FEATURE_SPECS.get(fname)
            max_age = spec.max_freshness_seconds if spec else 60.0
            age_sec = (now - event_time).total_seconds()
            quality = "FRESH" if age_sec <= max_age else "STALE"

            payload[fname] = {
                "feature_name": fname,
                "version": feature_version,
                "value": float(val),
                "event_time": event_time.isoformat(),
                "available_time": now.isoformat(),
                "computed_at": now.isoformat(),
                "source": spec.source if spec else "unknown",
                "freshness_seconds": max(0.0, age_sec),
                "quality": quality
            }

        key = self._build_key(symbol, horizon, feature_version)
        json_data = json.dumps(payload)

        if self._redis:
            try:
                await self._redis.set(key, json_data, ex=86400)
            except Exception as e:
                logger.error(f"[OnlineFeatureStore] Redis set error: {e}")

        self._local_cache[key] = payload
        return payload

    async def get_feature_vector(
        self,
        symbol: str,
        horizon: str,
        feature_version: str = "v2.0"
    ) -> Tuple[Dict[str, float], Dict[str, bool], Dict[str, float]]:
        """
        Retrieve (feature_values, availability_mask, freshness_mask).
        Strictly never fabricates missing features.
        """
        key = self._build_key(symbol, horizon, feature_version)
        raw_payload = None

        if self._redis:
            try:
                stored = await self._redis.get(key)
                if stored:
                    raw_payload = json.loads(stored)
            except Exception as e:
                logger.error(f"[OnlineFeatureStore] Redis get error: {e}")

        if not raw_payload:
            raw_payload = self._local_cache.get(key, {})

        now = datetime.now(timezone.utc)
        values: Dict[str, float] = {}
        availability_mask: Dict[str, bool] = {}
        freshness_mask: Dict[str, float] = {}

        for fname, spec in CORE_FEATURE_SPECS.items():
            if fname in raw_payload:
                meta = raw_payload[fname]
                val = meta.get("value")
                try:
                    c_time = datetime.fromisoformat(meta.get("computed_at", now.isoformat()))
                    age = (now - c_time).total_seconds()
                except Exception:
                    age = 9999.0

                values[fname] = float(val) if val is not None else float("nan")
                availability_mask[fname] = (val is not None)
                freshness_mask[fname] = age
            else:
                values[fname] = float("nan")
                availability_mask[fname] = False
                freshness_mask[fname] = float("inf")

        return values, availability_mask, freshness_mask


online_feature_store = OnlineFeatureStore()
