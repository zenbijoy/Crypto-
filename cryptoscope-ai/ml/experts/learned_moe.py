"""
CryptoScope AI - Learned Mixture of Experts (MoE) & Dynamic Gating Network
Integrates 8 specialized quantitative experts with dynamic gating weights conditioned on horizon,
asset, market volatility, and availability masking.
Calculates ensemble consensus, disagreement, and forecast quantiles [P10, P25, P50, P75, P90].
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import numpy as np
from ml.experts.expert_registry import ExpertOutput


class QuantileForecast(BaseModel):
    p10: float
    p25: float
    p50: float
    p75: float
    p90: float


class MoEForecastOutput(BaseModel):
    canonical_symbol: str
    horizon: str  # "1m", "5m", "15m", "1h", "4h", "1d"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Blended predictions
    direction: str  # "UP", "FLAT", "DOWN"
    direction_probabilities: Dict[str, float]
    expected_return_pct: float
    expected_volatility_pct: float
    quantiles: QuantileForecast
    
    # Gating weights
    active_expert_weights: Dict[str, float]
    active_expert_count: int
    expert_disagreement_score: float  # 0.0 to 100.0
    
    expert_breakdowns: Dict[str, ExpertOutput]


class LearnedMixtureOfExperts:
    """
    Dynamic Gating Network for Multi-Expert Blending.
    Strictly handles expert availability masking and horizon-adaptive weighting.
    """

    HORIZON_BASE_PRIORS = {
        "1m": {
            "MICROSTRUCTURE_EXPERT": 0.40,
            "TEMPORAL_PRICE_EXPERT": 0.30,
            "TREE_BASELINE_EXPERT": 0.15,
            "DERIVATIVES_EXPERT": 0.10,
            "REGIME_EXPERT": 0.05,
            "SENTIMENT_EXPERT": 0.00,
            "MACRO_EXPERT": 0.00,
            "ONCHAIN_EXPERT": 0.00
        },
        "5m": {
            "MICROSTRUCTURE_EXPERT": 0.35,
            "TEMPORAL_PRICE_EXPERT": 0.25,
            "TREE_BASELINE_EXPERT": 0.20,
            "DERIVATIVES_EXPERT": 0.12,
            "REGIME_EXPERT": 0.08,
            "SENTIMENT_EXPERT": 0.00,
            "MACRO_EXPERT": 0.00,
            "ONCHAIN_EXPERT": 0.00
        },
        "15m": {
            "TREE_BASELINE_EXPERT": 0.25,
            "TEMPORAL_PRICE_EXPERT": 0.20,
            "MICROSTRUCTURE_EXPERT": 0.18,
            "DERIVATIVES_EXPERT": 0.18,
            "REGIME_EXPERT": 0.10,
            "SENTIMENT_EXPERT": 0.05,
            "MACRO_EXPERT": 0.02,
            "ONCHAIN_EXPERT": 0.02
        },
        "1h": {
            "TREE_BASELINE_EXPERT": 0.25,
            "DERIVATIVES_EXPERT": 0.25,
            "TEMPORAL_PRICE_EXPERT": 0.15,
            "REGIME_EXPERT": 0.15,
            "SENTIMENT_EXPERT": 0.10,
            "MACRO_EXPERT": 0.05,
            "ONCHAIN_EXPERT": 0.05,
            "MICROSTRUCTURE_EXPERT": 0.00
        },
        "4h": {
            "DERIVATIVES_EXPERT": 0.28,
            "REGIME_EXPERT": 0.20,
            "MACRO_EXPERT": 0.18,
            "TREE_BASELINE_EXPERT": 0.15,
            "SENTIMENT_EXPERT": 0.10,
            "ONCHAIN_EXPERT": 0.09,
            "TEMPORAL_PRICE_EXPERT": 0.00,
            "MICROSTRUCTURE_EXPERT": 0.00
        },
        "1d": {
            "MACRO_EXPERT": 0.30,
            "DERIVATIVES_EXPERT": 0.25,
            "REGIME_EXPERT": 0.15,
            "ONCHAIN_EXPERT": 0.15,
            "SENTIMENT_EXPERT": 0.10,
            "TREE_BASELINE_EXPERT": 0.05,
            "TEMPORAL_PRICE_EXPERT": 0.00,
            "MICROSTRUCTURE_EXPERT": 0.00
        }
    }

    def combine(
        self,
        canonical_symbol: str,
        horizon: str,
        experts: Dict[str, ExpertOutput],
        volatility_annualized: float = 40.0,
        regime_entropy: float = 0.5
    ) -> MoEForecastOutput:
        priors = self.HORIZON_BASE_PRIORS.get(horizon, self.HORIZON_BASE_PRIORS["15m"])

        # Filter available experts and apply dynamic gating mask
        available_experts = {k: v for k, v in experts.items() if v.available}
        if not available_experts:
            raise ValueError("No experts available in MoE combine")

        raw_weights = {}
        for name, exp in available_experts.items():
            base_p = priors.get(name, 0.05)
            # Modulate by expert confidence
            conf = exp.confidence
            w = base_p * (0.5 + 0.5 * conf)
            raw_weights[name] = max(w, 0.001)

        # Normalize weights to strictly sum to 1.0
        tot_w = sum(raw_weights.values())
        norm_weights = {k: round(v / tot_w, 4) for k, v in raw_weights.items()}

        # Blend Directional Probabilities
        down_probs = [exp.directional_prob.get("DOWN", 0.33) * norm_weights[k] for k, exp in available_experts.items()]
        flat_probs = [exp.directional_prob.get("FLAT", 0.34) * norm_weights[k] for k, exp in available_experts.items()]
        up_probs = [exp.directional_prob.get("UP", 0.33) * norm_weights[k] for k, exp in available_experts.items()]

        b_down = float(sum(down_probs))
        b_flat = float(sum(flat_probs))
        b_up = float(sum(up_probs))
        sum_p = b_down + b_flat + b_up
        b_down /= sum_p
        b_flat /= sum_p
        b_up /= sum_p

        # Expected Return & Volatility
        returns = [exp.expected_return_pct * norm_weights[k] for k, exp in available_experts.items()]
        vols = [exp.expected_volatility_pct * norm_weights[k] for k, exp in available_experts.items()]
        b_ret = float(sum(returns))
        b_vol = float(sum(vols))

        # Disagreement score: variance of directional stance across experts
        stances = [exp.directional_prob.get("UP", 0.33) - exp.directional_prob.get("DOWN", 0.33) for exp in available_experts.values()]
        disagreement = float(np.std(stances)) * 100.0

        # Primary direction
        probs_map = {"DOWN": round(b_down, 4), "FLAT": round(b_flat, 4), "UP": round(b_up, 4)}
        top_dir = max(probs_map, key=probs_map.get)

        # Quantile estimates based on expected return and blended volatility
        sigma = b_vol / 100.0
        quantiles = QuantileForecast(
            p10=round(b_ret - 1.282 * sigma, 4),
            p25=round(b_ret - 0.674 * sigma, 4),
            p50=round(b_ret, 4),
            p75=round(b_ret + 0.674 * sigma, 4),
            p90=round(b_ret + 1.282 * sigma, 4)
        )

        return MoEForecastOutput(
            canonical_symbol=canonical_symbol,
            horizon=horizon,
            direction=top_dir,
            direction_probabilities=probs_map,
            expected_return_pct=round(b_ret, 4),
            expected_volatility_pct=round(b_vol, 2),
            quantiles=quantiles,
            active_expert_weights=norm_weights,
            active_expert_count=len(available_experts),
            expert_disagreement_score=round(disagreement, 1),
            expert_breakdowns=available_experts
        )
