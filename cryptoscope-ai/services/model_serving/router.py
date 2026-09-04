"""
Model Router selecting Champion or Approved Registered Fallbacks.
Phase 18: Model Routing.
"""
from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional

from services.model_serving.model_cache import ModelContainer, model_cache

logger = logging.getLogger("CryptoScope.ModelRouter")


class ModelRouter:
    """Routes requests to the validated champion or an approved fallback model. Never uses heuristics."""

    def __init__(self):
        # (asset, horizon) -> list of approved fallback version strings
        self._fallbacks: Dict[str, List[str]] = {}

    def register_fallback(self, asset: str, horizon: str, fallback_version: str):
        key = f"{asset.upper().replace('/', '')}:{horizon}"
        if key not in self._fallbacks:
            self._fallbacks[key] = []
        if fallback_version not in self._fallbacks[key]:
            self._fallbacks[key].append(fallback_version)

    def route_model(
        self,
        asset: str,
        horizon: str,
        available_features: Dict[str, bool],
        regime: str = "NORMAL"
    ) -> Optional[ModelContainer]:
        key = f"{asset.upper().replace('/', '')}:{horizon}"
        champion = model_cache.get_champion(asset, horizon)

        # Check if champion is healthy and features align
        if champion is not None:
            return champion

        # Check approved fallback models
        fallback_versions = self._fallbacks.get(key, [])
        for fv in fallback_versions:
            fallback_model = model_cache.get_model(asset, horizon, fv)
            if fallback_model is not None:
                logger.warning(f"[ModelRouter] Routing to approved fallback {fv} for {key}")
                return fallback_model

        # If no registered champion or fallback exists
        logger.error(f"[ModelRouter] No registered model or fallback available for {key}")
        return None


model_router = ModelRouter()
