"""
CryptoScope AI - Layer 6: Meta Ensemble & Model Agreement Engine
Combines Specialist Models (Tabular XGB, Orderflow TCN, Temporal TFT, Derivatives, Context)
with dynamic regime weighting and computes strict inter-model consensus / agreement metrics.
"""
import statistics
import math
from typing import Dict, Any, List

from ml.models.tabular_expert import tabular_expert
from ml.models.orderflow_tcn import orderflow_tcn_expert
from ml.models.temporal_tft import temporal_transformer_expert
from ml.models.derivatives_expert import derivatives_expert
from ml.models.context_expert import context_expert

class MetaEnsembleEngine:
    def __init__(self):
        self.tabular = tabular_expert
        self.orderflow = orderflow_tcn_expert
        self.temporal = temporal_transformer_expert
        self.derivatives = derivatives_expert
        self.context = context_expert

    def predict_ensemble(self, feature_vector: Dict[str, Any], horizon: str = "1h") -> Dict[str, Any]:
        """
        Executes all specialist models, computes agreement metric, dynamically weights according to
        detected market regime, and outputs combined ensemble prediction.
        """
        p_tab = self.tabular.predict(feature_vector)
        p_flow = self.orderflow.predict(feature_vector)
        p_temp = self.temporal.predict(feature_vector, horizon=horizon)
        p_deriv = self.derivatives.predict(feature_vector)
        p_ctx = self.context.predict(feature_vector)

        specialist_outputs = [p_tab, p_flow, p_temp, p_deriv, p_ctx]

        # 1. Determine Market Regime & Dynamic Weights
        deriv_info = feature_vector.get("derivatives", {})
        price_feats = feature_vector.get("price_features", {})
        vol_24h = price_feats.get("realized_volatility_24h", 0.02)
        price_oi_regime = deriv_info.get("price_oi_regime", "NEUTRAL")

        # Dynamic weights assignment
        if vol_24h > 0.04 or "LIQUIDATION" in price_oi_regime:
            # High Volatility / Liquidation Regime: Derivatives & Orderflow take priority
            weights = [0.15, 0.30, 0.15, 0.30, 0.10]
            current_regime = "HIGH_VOLATILITY_LIQUIDATION"
        elif abs(price_feats.get("return_24h_pct", 0.0)) > 3.5:
            # Strong Trending Regime: Temporal TFT & Tabular take priority
            weights = [0.30, 0.15, 0.35, 0.10, 0.10]
            current_regime = "TRENDING_MOMENTUM"
        else:
            # Mean Reverting / Normal Regime: Balanced weighting
            weights = [0.25, 0.25, 0.20, 0.20, 0.10]
            current_regime = "BALANCED_RANGE"

        # 2. Weighted probability aggregation
        w_up = sum(s["probabilities"]["up"] * w for s, w in zip(specialist_outputs, weights))
        w_down = sum(s["probabilities"]["down"] * w for s, w in zip(specialist_outputs, weights))
        w_neutral = sum(s["probabilities"]["neutral"] * w for s, w in zip(specialist_outputs, weights))
        tot = w_up + w_down + w_neutral
        p_up = w_up / tot
        p_down = w_down / tot
        p_neutral = w_neutral / tot

        # 3. Model Agreement Metric: 1.0 - StdDev(P_up_1, ..., P_up_n)
        up_probabilities = [s["probabilities"]["up"] for s in specialist_outputs]
        std_p_up = statistics.stdev(up_probabilities) if len(up_probabilities) > 1 else 0.0
        # Agreement scaled between 0.0 and 1.0
        agreement_score = max(0.0, min(1.0, 1.0 - (std_p_up * 2.0)))

        # 4. Expected return & Quantiles
        expected_log_return = sum(s.get("expected_log_return", 0.0) * w for s, w in zip(specialist_outputs, weights))
        close = price_feats.get("close", 67500.0)
        expected_price = close * math.exp(expected_log_return)

        # Quantile head from temporal specialist
        quantiles = p_temp.get("price_quantiles", {
            "p10": close * 0.98,
            "p25": close * 0.99,
            "p50": close,
            "p75": close * 1.01,
            "p90": close * 1.02
        })

        return {
            "regime": current_regime,
            "weights": {
                "tabular": weights[0],
                "orderflow": weights[1],
                "temporal": weights[2],
                "derivatives": weights[3],
                "context": weights[4]
            },
            "ensemble_probabilities": {
                "up": round(p_up, 4),
                "neutral": round(p_neutral, 4),
                "down": round(p_down, 4)
            },
            "model_agreement": round(agreement_score, 3),
            "expected_log_return": round(expected_log_return, 6),
            "expected_price": round(expected_price, 4),
            "price_quantiles": quantiles,
            "specialist_outputs": {s["expert_name"]: s for s in specialist_outputs}
        }

meta_ensemble_engine = MetaEnsembleEngine()
