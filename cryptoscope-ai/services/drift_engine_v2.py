"""
CryptoScope AI - Drift Engine V2 & Population Stability Index (PSI)
Detects distribution shift between training baseline and production inference features.
Calculates feature-level and model-level PSI, flagging retraining requirements.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import numpy as np


class DriftReport(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    overall_psi: float
    drift_status: str  # "NORMAL" (PSI < 0.1), "MODERATE_DRIFT" (0.1 <= PSI < 0.25), "CRITICAL_DRIFT" (PSI >= 0.25)
    retraining_required: bool
    feature_psi_breakdown: Dict[str, float]
    recommendation: str


class DriftEngineV2:
    @staticmethod
    def calculate_psi(baseline: np.ndarray, current: np.ndarray, num_bins: int = 10) -> float:
        """
        Calculates Population Stability Index:
        PSI = sum((actual% - expected%) * ln(actual% / expected%))
        """
        if len(baseline) < 20 or len(current) < 20:
            return 0.0

        # Create quantiles from baseline
        quantiles = np.linspace(0, 100, num_bins + 1)
        bins = np.percentile(baseline, quantiles)
        bins[0] -= 1e-5
        bins[-1] += 1e-5

        base_counts, _ = np.histogram(baseline, bins=bins)
        curr_counts, _ = np.histogram(current, bins=bins)

        base_pct = (base_counts / len(baseline)) + 1e-4
        curr_pct = (curr_counts / len(current)) + 1e-4

        psi = np.sum((curr_pct - base_pct) * np.log(curr_pct / base_pct))
        return float(psi)

    def evaluate_drift(
        self,
        baseline_features: Dict[str, np.ndarray],
        production_features: Dict[str, np.ndarray]
    ) -> DriftReport:
        psi_map = {}
        for feat_name, base_arr in baseline_features.items():
            if feat_name in production_features:
                psi_map[feat_name] = round(
                    self.calculate_psi(base_arr, production_features[feat_name]), 4
                )

        if not psi_map:
            return DriftReport(
                overall_psi=0.0,
                drift_status="NORMAL",
                retraining_required=False,
                feature_psi_breakdown={},
                recommendation="Insufficient features to evaluate drift"
            )

        mean_psi = float(np.mean(list(psi_map.values())))

        if mean_psi >= 0.25:
            status = "CRITICAL_DRIFT"
            retrain = True
            recom = "Critical distribution shift detected (PSI >= 0.25). Immediate model retraining recommended."
        elif mean_psi >= 0.10:
            status = "MODERATE_DRIFT"
            retrain = False
            recom = "Moderate feature drift detected (0.10 <= PSI < 0.25). Monitor performance and queue retraining."
        else:
            status = "NORMAL"
            retrain = False
            recom = "Feature distributions are stable within expected statistical bounds."

        return DriftReport(
            overall_psi=round(mean_psi, 4),
            drift_status=status,
            retraining_required=retrain,
            feature_psi_breakdown=psi_map,
            recommendation=recom
        )
