"""
CryptoScope AI - Uncertainty Engine V2
Synthesizes 5 distinct dimensions of uncertainty:
1. Model Softmax Entropy
2. Inter-Expert Disagreement
3. Quantile Dispersion (P90 - P10 width)
4. Market Regime Entropy & Stress
5. Data Ingestion Quality & Feed Latency
Produces canonical MODEL_UNCERTAINTY_SCORE (0 to 100).
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import numpy as np


class UncertaintyStateV2(BaseModel):
    canonical_symbol: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    model_uncertainty_score: float  # 0.0 to 100.0
    uncertainty_regime: str         # "LOW", "MODERATE", "HIGH", "CRITICAL_ABSTAIN"
    
    entropy_component: float        # 0.0 to 100.0
    disagreement_component: float   # 0.0 to 100.0
    dispersion_component: float     # 0.0 to 100.0
    regime_stress_component: float  # 0.0 to 100.0
    data_quality_penalty: float     # 0.0 to 100.0
    
    can_trade: bool
    abstention_reason: Optional[str] = None


class UncertaintyEngineV2:
    def __init__(self, critical_threshold: float = 65.0):
        self.critical_threshold = critical_threshold

    def compute(
        self,
        canonical_symbol: str,
        direction_probs: Dict[str, float],
        expert_disagreement: float,
        quantile_width_pct: float,
        regime_entropy: float,
        market_stress: float,
        data_quality: float = 100.0
    ) -> UncertaintyStateV2:
        # 1. Softmax entropy (max entropy for 3 classes is log(3) = 1.0986)
        p_vals = np.array(list(direction_probs.values()))
        p_vals = p_vals[p_vals > 1e-9]
        entropy = -np.sum(p_vals * np.log(p_vals))
        norm_entropy = min((entropy / np.log(3.0)) * 100.0, 100.0)

        # 2. Expert disagreement
        norm_disagree = min(expert_disagreement * 2.0, 100.0)

        # 3. Quantile dispersion
        norm_dispersion = min(quantile_width_pct * 120.0, 100.0)

        # 4. Regime stress & entropy
        regime_comp = min(regime_entropy * 50.0 + market_stress * 0.5, 100.0)

        # 5. Data quality penalty
        quality_penalty = max((100.0 - data_quality) * 1.5, 0.0)

        # Weighted aggregate
        total_score = (
            norm_entropy * 0.25 +
            norm_disagree * 0.25 +
            norm_dispersion * 0.20 +
            regime_comp * 0.20 +
            quality_penalty * 0.10
        )
        total_score = round(min(max(total_score, 0.0), 100.0), 1)

        # Classification
        if total_score >= self.critical_threshold or quality_penalty >= 50.0:
            regime = "CRITICAL_ABSTAIN"
            can_trade = False
            reason = f"Uncertainty score {total_score} exceeds threshold {self.critical_threshold}"
        elif total_score >= 50.0:
            regime = "HIGH"
            can_trade = True
            reason = "High uncertainty; size reduction advised"
        elif total_score >= 30.0:
            regime = "MODERATE"
            can_trade = True
            reason = None
        else:
            regime = "LOW"
            can_trade = True
            reason = None

        return UncertaintyStateV2(
            canonical_symbol=canonical_symbol,
            model_uncertainty_score=total_score,
            uncertainty_regime=regime,
            entropy_component=round(norm_entropy, 1),
            disagreement_component=round(norm_disagree, 1),
            dispersion_component=round(norm_dispersion, 1),
            regime_stress_component=round(regime_comp, 1),
            data_quality_penalty=round(quality_penalty, 1),
            can_trade=can_trade,
            abstention_reason=reason
        )
