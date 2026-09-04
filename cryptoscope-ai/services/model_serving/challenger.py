"""
Challenger Framework & Shadow Model Inference Routing.
Phase 19 & 20: Shadow Routing and Challenger Framework.
"""
from __future__ import annotations
import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from services.model_serving.inference import inference_pipeline
from services.model_serving.model_cache import model_cache

logger = logging.getLogger("CryptoScope.ChallengerFramework")


class ShadowInferenceRecord(BaseModel):
    record_id: str
    asset: str
    horizon: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    feature_snapshot_hash: str
    champion_model_id: str
    champion_prediction: Dict[str, float]
    challenger_model_id: str
    challenger_prediction: Dict[str, float]
    divergence_score: float  # Absolute probability delta between champion and challenger


class ChallengerFramework:
    """Manages active challengers per asset x horizon, running shadow inference in parallel."""

    def __init__(self):
        # (asset, horizon) -> list of challenger model IDs
        self._challengers: Dict[str, List[str]] = {}
        self._shadow_history: List[ShadowInferenceRecord] = []
        self._max_history = 1000

    def register_challenger(self, asset: str, horizon: str, challenger_version: str):
        key = f"{asset.upper().replace('/', '')}:{horizon}"
        if key not in self._challengers:
            self._challengers[key] = []
        if challenger_version not in self._challengers[key]:
            self._challengers[key].append(challenger_version)
            logger.info(f"[Challenger] Registered challenger {challenger_version} for {key}")

    async def execute_shadow_inference(
        self,
        asset: str,
        horizon: str,
        features: Dict[str, float],
        champion_prediction: Dict[str, float],
        champion_id: str
    ) -> List[ShadowInferenceRecord]:
        key = f"{asset.upper().replace('/', '')}:{horizon}"
        challenger_versions = self._challengers.get(key, [])
        if not challenger_versions:
            return []

        # Hash features snapshot
        feat_str = json.dumps(features, sort_keys=True)
        feat_hash = hashlib.sha256(feat_str.encode("utf-8")).hexdigest()[:16]

        records = []
        for cv in challenger_versions:
            challenger_container = model_cache.get_model(asset, horizon, cv)
            if not challenger_container:
                continue

            # Run shadow inference asynchronously without blocking user response
            challenger_pred, _ = inference_pipeline.run_inference(features, challenger_container)

            # Compute divergence
            div = abs(champion_prediction.get("p_up", 0.33) - challenger_pred.get("p_up", 0.33)) + \
                  abs(champion_prediction.get("p_down", 0.33) - challenger_pred.get("p_down", 0.33))

            rec = ShadowInferenceRecord(
                record_id=f"sh_{int(datetime.now(timezone.utc).timestamp()*1000)}_{cv[:6]}",
                asset=asset,
                horizon=horizon,
                feature_snapshot_hash=feat_hash,
                champion_model_id=champion_id,
                champion_prediction=champion_prediction,
                challenger_model_id=challenger_container.model_id,
                challenger_prediction=challenger_pred,
                divergence_score=round(div, 4)
            )
            records.append(rec)
            self._shadow_history.append(rec)
            if len(self._shadow_history) > self._max_history:
                self._shadow_history.pop(0)

        return records

    def get_shadow_metrics(self, asset: str, horizon: str) -> Dict[str, Any]:
        records = [r for r in self._shadow_history if r.asset == asset and r.horizon == horizon]
        if not records:
            return {"sample_count": 0, "mean_divergence": 0.0}
        mean_div = sum(r.divergence_score for r in records) / len(records)
        return {
            "sample_count": len(records),
            "mean_divergence": round(mean_div, 4),
            "latest_record": records[-1].model_dump() if records else None
        }


challenger_framework = ChallengerFramework()
