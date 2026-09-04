"""
Model Degradation Detector & Multi-Level Automatic Safety Response.
Phase 44 & 45: Degradation Detector & Safety Automation.
"""
from __future__ import annotations
import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from services.observability.performance_monitor import RollingPerformanceMetrics

logger = logging.getLogger("CryptoScope.DegradationDetector")


class SafetyLevel(int, Enum):
    NORMAL = 0
    LEVEL_1_REDUCE_CONFIDENCE = 1
    LEVEL_2_INCREASE_NO_TRADE = 2
    LEVEL_3_DISABLE_SIGNAL_CLASS = 3
    LEVEL_4_DISABLE_MODEL_FALLBACK = 4


class SafetyDecisionRecord(BaseModel):
    decision_id: str
    asset: str
    horizon: str
    safety_level: SafetyLevel
    actions_taken: List[str]
    trigger_metric: str
    metric_value: float
    benchmark_value: float
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class DegradationDetector:
    """Monitors rolling statistical metrics against baseline benchmarks and triggers automatic graded safety responses."""

    def __init__(
        self,
        baseline_mcc: float = 0.10,
        baseline_brier: float = 0.21,
        min_sample_size: int = 50
    ):
        self.baseline_mcc = baseline_mcc
        self.baseline_brier = baseline_brier
        self.min_sample_size = min_sample_size
        self._active_safety_levels: Dict[str, SafetyLevel] = {}
        self.safety_log: List[SafetyDecisionRecord] = []

    def evaluate_degradation(
        self,
        asset: str,
        horizon: str,
        metrics: RollingPerformanceMetrics
    ) -> Tuple[SafetyLevel, List[str]]:
        key = f"{asset.upper().replace('/', '')}:{horizon}"

        # Guard against small samples
        if metrics.sample_count < self.min_sample_size:
            self._active_safety_levels[key] = SafetyLevel.NORMAL
            return SafetyLevel.NORMAL, ["Sample size insufficient for degradation trigger"]

        level = SafetyLevel.NORMAL
        actions = []
        trigger_metric = "NONE"
        val = 0.0
        bench = 0.0

        # Severity assessment:
        # Severe degradation: Negative MCC or Brier > 0.28 -> LEVEL 4
        if metrics.mcc < -0.02 or metrics.brier_score > 0.28:
            level = SafetyLevel.LEVEL_4_DISABLE_MODEL_FALLBACK
            actions = [
                "Disable active model from primary serving",
                "Trigger automatic fallback to registered conservative champion",
                "Alert MLOps team"
            ]
            trigger_metric = "SEVERE_MCC_COLLAPSE" if metrics.mcc < -0.02 else "SEVERE_BRIER_DEGRADATION"
            val = metrics.mcc if metrics.mcc < -0.02 else metrics.brier_score
            bench = self.baseline_mcc

        # Moderate degradation: MCC collapsed by > 75% -> LEVEL 3
        elif metrics.mcc < (self.baseline_mcc * 0.25):
            level = SafetyLevel.LEVEL_3_DISABLE_SIGNAL_CLASS
            actions = [
                "Disable directional signal class (force NO_TRADE on all horizons)",
                "Retain feature store and shadow evaluations"
            ]
            trigger_metric = "MCC_COLLAPSE"
            val = metrics.mcc
            bench = self.baseline_mcc

        # Mild degradation: MCC dropped by 50% -> LEVEL 2
        elif metrics.mcc < (self.baseline_mcc * 0.50):
            level = SafetyLevel.LEVEL_2_INCREASE_NO_TRADE
            actions = [
                "Increase NO_TRADE threshold from 65% to 78%",
                "Constrain conviction score scaling"
            ]
            trigger_metric = "MCC_DROP"
            val = metrics.mcc
            bench = self.baseline_mcc

        # Borderline: Brier score above benchmark -> LEVEL 1
        elif metrics.brier_score > self.baseline_brier * 1.15:
            level = SafetyLevel.LEVEL_1_REDUCE_CONFIDENCE
            actions = [
                "Apply 20% dampener to confidence score",
                "Mark output status as DEGRADED"
            ]
            trigger_metric = "BRIER_ELEVATION"
            val = metrics.brier_score
            bench = self.baseline_brier

        self._active_safety_levels[key] = level

        if level != SafetyLevel.NORMAL:
            rec = SafetyDecisionRecord(
                decision_id=f"safe_{int(datetime.now(timezone.utc).timestamp())}",
                asset=asset,
                horizon=horizon,
                safety_level=level,
                actions_taken=actions,
                trigger_metric=trigger_metric,
                metric_value=round(val, 4),
                benchmark_value=round(bench, 4)
            )
            self.safety_log.append(rec)
            logger.warning(
                f"[DegradationDetector] Triggered {level.name} for {key}: "
                f"{trigger_metric}={val:.4f} (Bench={bench:.4f})"
            )

        return level, actions

    def get_safety_level(self, asset: str, horizon: str) -> SafetyLevel:
        key = f"{asset.upper().replace('/', '')}:{horizon}"
        return self._active_safety_levels.get(key, SafetyLevel.NORMAL)


degradation_detector = DegradationDetector()
