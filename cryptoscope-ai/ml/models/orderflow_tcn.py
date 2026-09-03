"""
CryptoScope AI - Layer 2: Heuristic Orderflow Baseline (Step 12)
Classified explicitly as EXPERIMENTAL_HEURISTIC baseline.
Not a trained Temporal Convolutional Network (TCN) deep learning artifact.
"""
import math
from typing import Dict, Any

class HeuristicOrderflowBaseline:
    def __init__(self, name: str = "HeuristicOrderflowBaseline"):
        self.name = name
        self.model_type = "EXPERIMENTAL_HEURISTIC"
        self.is_trained_deep_learning = False
        self.is_heuristic_baseline = True

    def predict(self, feature_vector: Dict[str, Any]) -> Dict[str, Any]:
        micro = feature_vector.get("microstructure")
        price_feats = feature_vector.get("price_features", {})
        close = price_feats.get("close")

        # If microstructure data is absent or invalid, abstain neutrally
        if not micro or not close:
            return {
                "expert_name": self.name,
                "model_type": self.model_type,
                "is_trained_deep_learning": False,
                "is_heuristic_baseline": True,
                "probabilities": {"up": 0.3333, "neutral": 0.3334, "down": 0.3333},
                "expected_log_return": 0.0,
                "microstructure_pressure": 0.0,
                "expert_confidence": 33.33,
                "status": "DATA_UNAVAILABLE"
            }

        mid = micro.get("microprice", close)
        spread_bps = micro.get("spread_bps", 1.5)
        obi_10bps = micro.get("orderbook_imbalance_10bps", 0.0)

        micro_drift = (mid - close) / close if close > 0 else 0.0
        flow_score = (obi_10bps * 0.55) + (micro_drift * 50.0 * 0.35)

        spread_factor = max(0.2, 1.0 - (spread_bps / 15.0))
        flow_score *= spread_factor

        logit_up = flow_score * 2.2
        logit_down = -flow_score * 2.2
        logit_neutral = max(0.0, 0.8 - abs(flow_score) * 1.2)

        exp_u = math.exp(logit_up)
        exp_d = math.exp(logit_down)
        exp_n = math.exp(logit_neutral)
        s = exp_u + exp_d + exp_n

        p_up = exp_u / s
        p_down = exp_d / s
        p_neutral = exp_n / s

        expected_log_return = (p_up - p_down) * 0.0045

        return {
            "expert_name": self.name,
            "model_type": self.model_type,
            "is_trained_deep_learning": False,
            "is_heuristic_baseline": True,
            "probabilities": {
                "up": round(p_up, 4),
                "neutral": round(p_neutral, 4),
                "down": round(p_down, 4)
            },
            "expected_log_return": round(expected_log_return, 6),
            "microstructure_pressure": round(obi_10bps, 3),
            "expert_confidence": round(float(max(p_up, p_down) * 100), 2),
            "status": "ACTIVE"
        }

# Alias for backward compatibility
OrderflowTCNExpert = HeuristicOrderflowBaseline
orderflow_expert = HeuristicOrderflowBaseline()
orderflow_tcn_expert = orderflow_expert

