"""
Model Canary Deployment and Observation Routing.
Phase 24: Model Canary.
"""
from __future__ import annotations
import logging
import random
from typing import Any, Dict, Optional, Tuple

from services.model_serving.inference import inference_pipeline
from services.model_serving.model_cache import ModelContainer, model_cache

logger = logging.getLogger("CryptoScope.Canary")


class CanaryRouter:
    """Routes a small percentage of inference requests (e.g. 5%) to candidate models for non-blocking observation."""

    def __init__(self, default_percentage: float = 5.0):
        self.default_percentage = default_percentage
        # (asset, horizon) -> {"candidate_version": str, "percentage": float}
        self._canary_configs: Dict[str, Dict[str, Any]] = {}
        self._canary_stats: Dict[str, Dict[str, int]] = {}

    def set_canary(self, asset: str, horizon: str, candidate_version: str, percentage: float = 5.0):
        key = f"{asset.upper().replace('/', '')}:{horizon}"
        self._canary_configs[key] = {
            "candidate_version": candidate_version,
            "percentage": max(0.0, min(100.0, percentage))
        }
        self._canary_stats[key] = {"total_routed": 0, "canary_routed": 0}
        logger.info(f"[CanaryRouter] Configured {percentage}% canary to {candidate_version} for {key}")

    def should_route_canary(self, asset: str, horizon: str) -> Tuple[bool, Optional[str]]:
        key = f"{asset.upper().replace('/', '')}:{horizon}"
        cfg = self._canary_configs.get(key)
        if not cfg:
            return False, None

        self._canary_stats[key]["total_routed"] += 1
        pct = cfg["percentage"]
        if random.random() * 100.0 < pct:
            self._canary_stats[key]["canary_routed"] += 1
            return True, cfg["candidate_version"]

        return False, None

    def get_stats(self, asset: str, horizon: str) -> Dict[str, Any]:
        key = f"{asset.upper().replace('/', '')}:{horizon}"
        cfg = self._canary_configs.get(key, {})
        stats = self._canary_stats.get(key, {"total_routed": 0, "canary_routed": 0})
        return {
            "configured": bool(cfg),
            "candidate_version": cfg.get("candidate_version"),
            "target_percentage": cfg.get("percentage", 0.0),
            "total_routed": stats["total_routed"],
            "canary_routed": stats["canary_routed"]
        }


canary_router = CanaryRouter()
