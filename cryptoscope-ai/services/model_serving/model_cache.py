"""
In-Memory Model Cache with Atomic Hot Swapping and Safe Reference Holding.
Phase 15 & 16: Model Cache & Safe Hot Swap.
"""
from __future__ import annotations
import asyncio
import logging
import time
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger("CryptoScope.ModelCache")


class ModelContainer:
    """Encapsulates a model instance with its metadata, schema, and preprocessor."""

    def __init__(self, model_id: str, model_obj: Any, metadata: Dict[str, Any]):
        self.model_id = model_id
        self.model = model_obj
        self.metadata = metadata
        self.loaded_at = time.time()
        self.inference_count = 0
        self._active_requests = 0
        self._lock = asyncio.Lock()

    async def acquire(self):
        async with self._lock:
            self._active_requests += 1
            self.inference_count += 1

    async def release(self):
        async with self._lock:
            self._active_requests = max(0, self._active_requests - 1)

    @property
    def is_in_use(self) -> bool:
        return self._active_requests > 0


class ModelCache:
    """Manages active models in memory with zero-downtime atomic hot swaps."""

    def __init__(self):
        # (asset, horizon) -> ModelContainer (champion)
        self._champions: Dict[Tuple[str, str], ModelContainer] = {}
        # (asset, horizon, version) -> ModelContainer
        self._pool: Dict[Tuple[str, str, str], ModelContainer] = {}
        self._swap_lock = asyncio.Lock()

    def register_model(
        self,
        asset: str,
        horizon: str,
        version: str,
        model_obj: Any,
        metadata: Dict[str, Any],
        is_champion: bool = False
    ) -> ModelContainer:
        clean_asset = asset.upper().replace("/", "")
        container = ModelContainer(f"{clean_asset}_{horizon}_{version}", model_obj, metadata)
        pool_key = (clean_asset, horizon, version)
        self._pool[pool_key] = container

        if is_champion or (clean_asset, horizon) not in self._champions:
            self._champions[(clean_asset, horizon)] = container
            logger.info(f"[ModelCache] Set initial champion for {clean_asset}:{horizon} -> {version}")

        return container

    def get_champion(self, asset: str, horizon: str) -> Optional[ModelContainer]:
        clean_asset = asset.upper().replace("/", "")
        return self._champions.get((clean_asset, horizon))

    def get_model(self, asset: str, horizon: str, version: str) -> Optional[ModelContainer]:
        clean_asset = asset.upper().replace("/", "")
        return self._pool.get((clean_asset, horizon, version))

    async def atomic_swap_champion(
        self,
        asset: str,
        horizon: str,
        new_version: str,
        candidate_model_obj: Any,
        metadata: Dict[str, Any]
    ) -> bool:
        """
        Deploy new champion atomically without downtime.
        Runs smoke inference before switching pointer.
        """
        clean_asset = asset.upper().replace("/", "")
        async with self._swap_lock:
            logger.info(f"[ModelCache] Initiating atomic hot swap for {clean_asset}:{horizon} to {new_version}")

            # 1. Instantiate new container
            new_container = ModelContainer(
                f"{clean_asset}_{horizon}_{new_version}",
                candidate_model_obj,
                metadata
            )

            # 2. Run smoke inference test
            try:
                # Expecting model object to support predict or predict_proba
                dummy_input = [[0.0] * 6]
                if hasattr(candidate_model_obj, "predict_proba"):
                    candidate_model_obj.predict_proba(dummy_input)
                elif hasattr(candidate_model_obj, "predict"):
                    candidate_model_obj.predict(dummy_input)
                logger.info(f"[ModelCache] Smoke inference passed for candidate {new_version}")
            except Exception as e:
                logger.error(f"[ModelCache] Hot swap aborted: smoke inference failed: {e}")
                return False

            # 3. Store in pool
            self._pool[(clean_asset, horizon, new_version)] = new_container

            # 4. Atomically point champion to new container
            old_champion = self._champions.get((clean_asset, horizon))
            self._champions[(clean_asset, horizon)] = new_container

            logger.info(
                f"[ModelCache] Successfully hot-swapped champion for {clean_asset}:{horizon} "
                f"from {old_champion.model_id if old_champion else 'NONE'} to {new_container.model_id}"
            )
            return True

    def stats(self) -> Dict[str, Any]:
        return {
            "champions_count": len(self._champions),
            "pool_size": len(self._pool),
            "active_models": [
                {
                    "key": f"{k[0]}:{k[1]}",
                    "model_id": v.model_id,
                    "inferences": v.inference_count,
                    "in_use": v.is_in_use
                }
                for k, v in self._champions.items()
            ]
        }


model_cache = ModelCache()
