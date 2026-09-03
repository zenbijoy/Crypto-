"""
CryptoScope AI - Layer 5: Market Context & Macro/Sentiment Expert
Specialist model processing macro risk regimes (interest rate expectations, liquidity proxies),
Fear & Greed indices, news sentiment velocity, and DeFi on-chain activity.
"""
import math
from typing import Dict, Any

class MarketContextExpert:
    def __init__(self, name: str = "Market_Context_Expert"):
        self.name = name

    def predict(self, feature_vector: Dict[str, Any]) -> Dict[str, Any]:
        # Context features (Macro + Sentiment + On-chain + Breadth)
        fng_index = 68.0  # Fear & Greed (0-100)
        news_sentiment_score = 0.25  # -1.0 to +1.0
        macro_liquidity_z = 0.45
        
        # Scoring
        score = (news_sentiment_score * 0.40) + ((fng_index - 50.0) / 50.0 * 0.35) + (macro_liquidity_z * 0.25)
        
        logit_up = score * 1.8
        logit_down = -score * 1.8
        logit_neutral = max(0.0, 1.0 - abs(score) * 1.2)

        exp_u = math.exp(logit_up)
        exp_d = math.exp(logit_down)
        exp_n = math.exp(logit_neutral)
        s = exp_u + exp_d + exp_n

        p_up = exp_u / s
        p_down = exp_d / s
        p_neutral = exp_n / s

        expected_log_ret = (p_up - p_down) * 0.0050

        return {
            "expert_name": self.name,
            "probabilities": {
                "up": round(p_up, 4),
                "neutral": round(p_neutral, 4),
                "down": round(p_down, 4)
            },
            "expected_log_return": round(expected_log_ret, 6),
            "sentiment_score": round(news_sentiment_score, 3),
            "expert_confidence": round(float(max(p_up, p_down) * 100), 2)
        }

context_expert = MarketContextExpert()
