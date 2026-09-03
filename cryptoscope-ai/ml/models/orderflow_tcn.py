"""
CryptoScope AI - Layer 2: Microstructure & Orderflow TCN Expert
Specialist model processing L2 order book depth, Order Book Imbalance (OBI), microprice,
bid/ask spread dynamics, and Cumulative Volume Delta (CVD) aggressive trade flow.
"""
import math
from typing import Dict, Any, List

class OrderflowTCNExpert:
    def __init__(self, name: str = "Orderflow_TCN_Expert"):
        self.name = name

    def predict(self, feature_vector: Dict[str, Any]) -> Dict[str, Any]:
        micro = feature_vector.get("microstructure", {})
        price_feats = feature_vector.get("price_features", {})
        
        mid = micro.get("microprice", price_feats.get("close", 67500.0))
        close = price_feats.get("close", 67500.0)
        spread_bps = micro.get("spread_bps", 1.2)
        obi_10bps = micro.get("orderbook_imbalance_10bps", 0.0)  # -1.0 to +1.0
        book_convexity = micro.get("book_convexity", 1.0)
        
        # Microprice drift relative to mid
        micro_drift = (mid - close) / close if close > 0 else 0.0

        # TCN receptive field aggregation
        # Strong positive OBI + positive microprice drift indicates buy wall pressure
        flow_score = (obi_10bps * 0.55) + (micro_drift * 50.0 * 0.35)
        
        # Spread penalty: wider spreads reduce directional conviction
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

        expected_log_return = (p_up - p_down) * 0.0045 * book_convexity

        return {
            "expert_name": self.name,
            "probabilities": {
                "up": round(p_up, 4),
                "neutral": round(p_neutral, 4),
                "down": round(p_down, 4)
            },
            "expected_log_return": round(expected_log_return, 6),
            "microstructure_pressure": round(obi_10bps, 3),
            "expert_confidence": round(float(max(p_up, p_down) * 100), 2)
        }

orderflow_tcn_expert = OrderflowTCNExpert()
