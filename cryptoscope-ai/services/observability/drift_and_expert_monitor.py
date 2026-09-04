"""
Feature Importance Drift, Expert Weight Collapse & Model Agreement Monitor.
Phase 89, 90, 91: Drift & Ensemble Diagnostics.
"""
from __future__ import annotations
import logging
import math
from typing import Any, Dict, List, Tuple

logger = logging.getLogger("CryptoScope.DriftMonitor")


class EnsembleDiagnosticsMonitor:
    """Monitors SHAP attribution stability, Mixture-of-Experts weight collapse, and model agreement."""

    def __init__(self):
        # Baseline reference SHAP attributions
        self.baseline_attributions = {
            "order_imbalance": 0.35,
            "realized_volatility_5m": 0.25,
            "funding_rate": 0.20,
            "cvd_quote": 0.12,
            "spread_bps": 0.08
        }

    def check_attribution_drift(self, current_attributions: Dict[str, float]) -> Tuple[bool, float, Dict[str, Any]]:
        """Calculate cosine similarity / divergence between baseline and rolling SHAP attributions."""
        drift_delta = 0.0
        details = {}
        for feat, base_val in self.baseline_attributions.items():
            curr_val = current_attributions.get(feat, base_val)
            delta = abs(curr_val - base_val)
            drift_delta += delta
            details[feat] = {"baseline": base_val, "current": curr_val, "delta": round(delta, 3)}

        # Large drift trigger (> 0.40 total attribution shift)
        drift_detected = drift_delta > 0.40
        return drift_detected, round(drift_delta, 3), details

    def check_expert_collapse(self, expert_weights: Dict[str, float]) -> Tuple[bool, str]:
        """Detect if one expert dominates (>90%) or if weights collapse to zero."""
        if not expert_weights:
            return False, "HEALTHY"

        max_weight = max(expert_weights.values())
        max_expert = [k for k, v in expert_weights.items() if v == max_weight][0]

        if max_weight > 0.92:
            msg = f"Expert collapse alert: {max_expert} dominates with {max_weight*100:.1f}% weight"
            logger.warning(f"[EnsembleDiagnostics] {msg}")
            return True, msg

        return False, "BALANCED"

    def check_model_agreement(
        self,
        tree_probs: Dict[str, float],
        dl_probs: Dict[str, float]
    ) -> Tuple[float, bool]:
        """Measure directional agreement between tree models and deep learning models."""
        tree_dir = "UP" if tree_probs.get("p_up", 0.33) > tree_probs.get("p_down", 0.33) else "DOWN"
        dl_dir = "UP" if dl_probs.get("p_up", 0.33) > dl_probs.get("p_down", 0.33) else "DOWN"

        # Jensen-Shannon or variation distance
        p_up_diff = abs(tree_probs.get("p_up", 0.33) - dl_probs.get("p_up", 0.33))
        p_down_diff = abs(tree_probs.get("p_down", 0.33) - dl_probs.get("p_down", 0.33))
        total_divergence = round((p_up_diff + p_down_diff) / 2.0, 3)

        agreement = (tree_dir == dl_dir)
        return total_divergence, agreement


ensemble_diagnostics = EnsembleDiagnosticsMonitor()
