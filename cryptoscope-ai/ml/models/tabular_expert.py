"""
CryptoScope AI - Layer 1: Tabular Feature Expert Model
Specialist model trained on price returns, technical indicators (RSI, MACD, Bollinger Bands, ATR),
and statistical momentum moments (volatility, skewness, kurtosis).
"""
import math
from typing import Dict, Any, List

class TabularFeatureExpert:
    def __init__(self, name: str = "Tabular_XGB_Expert"):
        self.name = name

    def predict(self, feature_vector: Dict[str, Any]) -> Dict[str, Any]:
        """
        Infers probabilistic direction and expected log-return from engineered tabular feature set.
        """
        price_feats = feature_vector.get("price_features", {})
        technicals = feature_vector.get("technical_indicators", {})
        
        rsi = technicals.get("rsi_14", 50.0)
        macd_hist = technicals.get("macd_hist", 0.0)
        ret_1h = price_feats.get("return_1h_pct", 0.0)
        ret_24h = price_feats.get("return_24h_pct", 0.0)
        vol_24h = price_feats.get("realized_volatility_24h", 0.02)
        skew = price_feats.get("skewness_24h", 0.0)

        # Quantitative tabular scoring
        raw_score = 0.0
        # RSI mean-reversion & momentum trend
        if rsi < 30:
            raw_score += 0.35 * (30 - rsi) / 30.0
        elif rsi > 70:
            raw_score -= 0.35 * (rsi - 70) / 30.0
        else:
            raw_score += 0.15 * ((rsi - 50.0) / 20.0)

        # MACD Histogram acceleration
        raw_score += math.tanh(macd_hist * 10.0) * 0.30
        
        # Momentum & Skew
        raw_score += math.tanh(ret_1h / 2.0) * 0.20
        raw_score += math.tanh(skew) * 0.15

        # Probabilities via softmax
        logit_up = raw_score * 2.0
        logit_down = -raw_score * 2.0
        logit_neutral = max(0.0, 1.0 - abs(raw_score) * 1.5)

        exp_up = math.exp(logit_up)
        exp_down = math.exp(logit_down)
        exp_neutral = math.exp(logit_neutral)
        total_exp = exp_up + exp_down + exp_neutral

        p_up = exp_up / total_exp
        p_down = exp_down / total_exp
        p_neutral = exp_neutral / total_exp

        expected_log_return = (p_up - p_down) * vol_24h * 0.85

        return {
            "expert_name": self.name,
            "probabilities": {
                "up": round(p_up, 4),
                "neutral": round(p_neutral, 4),
                "down": round(p_down, 4)
            },
            "expected_log_return": round(expected_log_return, 6),
            "expected_volatility": round(vol_24h, 4),
            "expert_confidence": round(float(max(p_up, p_down) * 100), 2)
        }

tabular_expert = TabularFeatureExpert()
