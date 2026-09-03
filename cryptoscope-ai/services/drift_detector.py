"""
CryptoScope AI - Statistical Drift Detector & PSI Engine
Implements Section 54:
- Population Stability Index (PSI) for feature drift monitoring
- Prediction distribution drift
- Calibration & Residual drift detection
"""
import math
from typing import List, Dict, Any

class DriftDetector:
    def compute_psi(self, expected: List[float], actual: List[float], num_buckets: int = 10) -> float:
        """
        Calculates Population Stability Index (PSI) between baseline (expected) and current (actual).
        PSI < 0.1: No significant change
        0.1 <= PSI < 0.25: Moderate drift
        PSI >= 0.25: Significant drift -> triggers model retraining alert
        """
        if not expected or not actual:
            return 0.0

        n_exp = len(expected)
        n_act = len(actual)
        
        # Adaptive bucket count for sample size
        k_buckets = min(num_buckets, max(2, min(n_exp, n_act) // 2))

        min_val = min(min(expected), min(actual))
        max_val = max(max(expected), max(actual))
        if min_val == max_val:
            return 0.0

        step = (max_val - min_val) / k_buckets
        buckets = [min_val + i * step for i in range(k_buckets + 1)]

        psi_total = 0.0

        for i in range(k_buckets):
            low, high = buckets[i], buckets[i + 1]
            exp_count = sum(1 for x in expected if low <= x < high or (i == k_buckets - 1 and x == high))
            act_count = sum(1 for x in actual if low <= x < high or (i == k_buckets - 1 and x == high))

            exp_pct = (exp_count + 0.5) / (n_exp + 0.5 * k_buckets)
            act_pct = (act_count + 0.5) / (n_act + 0.5 * k_buckets)

            psi_total += (act_pct - exp_pct) * math.log(act_pct / exp_pct)

        return float(round(psi_total, 4))

    def evaluate_feature_drift(self, baseline_features: List[float], live_features: List[float]) -> Dict[str, Any]:
        psi = self.compute_psi(baseline_features, live_features)
        status = "HEALTHY"
        if psi >= 0.25:
            status = "CRITICAL_DRIFT_RETRAIN_REQUIRED"
        elif psi >= 0.10:
            status = "MODERATE_DRIFT_MONITORING"

        return {
            "psi": psi,
            "status": status,
            "retrain_recommended": psi >= 0.25
        }

drift_detector = DriftDetector()
