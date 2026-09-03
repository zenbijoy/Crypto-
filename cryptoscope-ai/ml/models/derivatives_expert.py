"""
CryptoScope AI - Layer 4: Derivatives Intelligence Expert
Specialist model processing Open Interest velocity, Funding Rate Z-score, Liquidation imbalance,
and Retail vs Whale Long/Short position divergence.
"""
import math
from typing import Dict, Any

class DerivativesExpert:
    def __init__(self, name: str = "Derivatives_Expert"):
        self.name = name

    def predict(self, feature_vector: Dict[str, Any]) -> Dict[str, Any]:
        deriv = feature_vector.get("derivatives", {})
        price_feats = feature_vector.get("price_features", {})
        
        funding_z = deriv.get("funding_zscore_7d", 0.0)
        oi_velocity = deriv.get("oi_velocity_24h_pct", 0.0)
        liq_pressure = deriv.get("liquidation_pressure_score", 50.0)
        regime = deriv.get("price_oi_regime", "NEUTRAL")
        
        # Derivatives signal calculation
        # High positive funding Z-score (> 2.0) with over-leveraged longs signals short squeeze exhaustion / long liquidation vulnerability
        # Negative funding Z-score (< -2.0) with rising OI signals short squeeze potential
        score = 0.0
        if regime == "LONG_ACCUMULATION":
            score += 0.40
        elif regime == "SHORT_SQUEEZE":
            score += 0.60
        elif regime == "SHORT_ACCUMULATION":
            score -= 0.40
        elif regime == "LONG_LIQUIDATION":
            score -= 0.60

        # Mean reversion on extreme funding
        if funding_z > 2.5:
            score -= 0.35  # Overheated longs
        elif funding_z < -2.5:
            score += 0.35  # Overheated shorts ready for squeeze

        logit_up = score * 2.0
        logit_down = -score * 2.0
        logit_neutral = max(0.0, 1.0 - abs(score) * 1.4)

        exp_u = math.exp(logit_up)
        exp_d = math.exp(logit_down)
        exp_n = math.exp(logit_neutral)
        s = exp_u + exp_d + exp_n

        p_up = exp_u / s
        p_down = exp_d / s
        p_neutral = exp_n / s

        expected_log_ret = (p_up - p_down) * 0.0075

        return {
            "expert_name": self.name,
            "probabilities": {
                "up": round(p_up, 4),
                "neutral": round(p_neutral, 4),
                "down": round(p_down, 4)
            },
            "expected_log_return": round(expected_log_ret, 6),
            "derivatives_regime": regime,
            "liquidation_pressure": liq_pressure,
            "expert_confidence": round(float(max(p_up, p_down) * 100), 2)
        }

derivatives_expert = DerivativesExpert()
