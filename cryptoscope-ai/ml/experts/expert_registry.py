"""
CryptoScope AI - Expert Registry & Domain Architecture
Defines the 8 specialized quantitative experts that feed into the Mixture of Experts:
1. TREE_BASELINE_EXPERT (XGBoost / LightGBM tabular signals)
2. TEMPORAL_PRICE_EXPERT (Causal TCN / GRU temporal sequence)
3. MICROSTRUCTURE_EXPERT (Order book depth, microprice, CVD, OBI)
4. DERIVATIVES_EXPERT (Cross-exchange funding divergence, OI acceleration, squeeze risk)
5. ONCHAIN_EXPERT (Mempool fees, TPS, chain activity)
6. MACRO_EXPERT (Yield curve, rate proxy, economic event proximity)
7. SENTIMENT_EXPERT (NLP news sentiment, urgency bursts)
8. REGIME_EXPERT (Market regime state & entropy)
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import numpy as np


class ExpertOutput(BaseModel):
    expert_name: str
    available: bool
    confidence: float  # 0.0 to 1.0
    directional_prob: Dict[str, float]  # "DOWN", "FLAT", "UP"
    expected_return_pct: float
    expected_volatility_pct: float
    reasoning: str


class ExpertRegistry:
    @staticmethod
    def evaluate_microstructure_expert(ob_feat: Any, of_feat: Any) -> ExpertOutput:
        """Microstructure Expert: evaluates OBI, microprice divergence, CVD imbalance."""
        if not ob_feat or not of_feat:
            return ExpertOutput(
                expert_name="MICROSTRUCTURE_EXPERT",
                available=False,
                confidence=0.0,
                directional_prob={"DOWN": 0.333, "FLAT": 0.334, "UP": 0.333},
                expected_return_pct=0.0,
                expected_volatility_pct=2.0,
                reasoning="Microstructure feeds unavailable"
            )

        obi = getattr(ob_feat, "obi_level_5", 0.0)
        micro_div = getattr(ob_feat, "microprice_divergence_bps", 0.0)
        flow_imb = getattr(of_feat, "volume_imbalance", 0.0)

        # Signal score (-1.0 to +1.0)
        signal = obi * 0.4 + np.clip(micro_div / 2.0, -1.0, 1.0) * 0.3 + flow_imb * 0.3
        
        up_prob = float(np.clip(0.333 + signal * 0.35, 0.05, 0.90))
        down_prob = float(np.clip(0.333 - signal * 0.35, 0.05, 0.90))
        flat_prob = float(max(1.0 - up_prob - down_prob, 0.05))
        # re-normalize
        tot = up_prob + down_prob + flat_prob
        
        conf = float(min(abs(signal) * 1.5 + 0.3, 1.0))
        ret = round(signal * 0.25, 4)

        return ExpertOutput(
            expert_name="MICROSTRUCTURE_EXPERT",
            available=True,
            confidence=round(conf, 3),
            directional_prob={"DOWN": round(down_prob / tot, 4), "FLAT": round(flat_prob / tot, 4), "UP": round(up_prob / tot, 4)},
            expected_return_pct=ret,
            expected_volatility_pct=1.8,
            reasoning=f"OBI={obi:.3f}, MicroDiv={micro_div:.2f}bps, FlowImb={flow_imb:.3f}"
        )

    @staticmethod
    def evaluate_derivatives_expert(funding_state: Any, oi_state: Any, deriv_state: Any) -> ExpertOutput:
        """Derivatives Expert: evaluates funding arbitrage, OI velocity, positioning squeeze."""
        if not funding_state or not deriv_state:
            return ExpertOutput(
                expert_name="DERIVATIVES_EXPERT",
                available=False,
                confidence=0.0,
                directional_prob={"DOWN": 0.333, "FLAT": 0.334, "UP": 0.333},
                expected_return_pct=0.0,
                expected_volatility_pct=2.0,
                reasoning="Derivatives feeds unavailable"
            )

        f_rate = getattr(funding_state, "mean_funding_rate", 0.0)
        f_regime = getattr(funding_state, "regime", "NEUTRAL")
        m_state = getattr(deriv_state, "state", "NEUTRAL")
        squeeze = getattr(deriv_state, "squeeze_risk", "LOW")

        # Directional mapping
        signal = 0.0
        if m_state == "NEW_LONG_EXPANSION":
            signal += 0.5
        elif m_state == "NEW_SHORT_EXPANSION":
            signal -= 0.5
        elif m_state == "SHORT_COVERING":
            signal += 0.3
        elif m_state == "LONG_LIQUIDATION":
            signal -= 0.4

        if squeeze == "HIGH_SHORT_SQUEEZE":
            signal += 0.4
        elif squeeze == "HIGH_LONG_SQUEEZE":
            signal -= 0.4

        up_p = float(np.clip(0.333 + signal * 0.35, 0.05, 0.90))
        down_p = float(np.clip(0.333 - signal * 0.35, 0.05, 0.90))
        flat_p = float(max(1.0 - up_p - down_p, 0.05))
        tot = up_p + down_p + flat_p

        return ExpertOutput(
            expert_name="DERIVATIVES_EXPERT",
            available=True,
            confidence=round(getattr(deriv_state, "state_confidence", 70.0) / 100.0, 3),
            directional_prob={"DOWN": round(down_p / tot, 4), "FLAT": round(flat_p / tot, 4), "UP": round(up_p / tot, 4)},
            expected_return_pct=round(signal * 0.3, 4),
            expected_volatility_pct=2.2,
            reasoning=f"State={m_state}, Squeeze={squeeze}, FundingRegime={f_regime}"
        )

    @staticmethod
    def evaluate_sentiment_expert(sentiment_feat: Any) -> ExpertOutput:
        """Sentiment Expert: evaluates NLP news sentiment score, velocity, urgency."""
        if not sentiment_feat:
            return ExpertOutput(
                expert_name="SENTIMENT_EXPERT",
                available=False,
                confidence=0.0,
                directional_prob={"DOWN": 0.333, "FLAT": 0.334, "UP": 0.333},
                expected_return_pct=0.0,
                expected_volatility_pct=2.0,
                reasoning="Sentiment feeds unavailable"
            )

        score = getattr(sentiment_feat, "current_sentiment_score", 0.0)
        vel = getattr(sentiment_feat, "sentiment_velocity", 0.0)
        signal = score * 0.7 + vel * 0.3

        up_p = float(np.clip(0.333 + signal * 0.3, 0.05, 0.90))
        down_p = float(np.clip(0.333 - signal * 0.3, 0.05, 0.90))
        flat_p = float(max(1.0 - up_p - down_p, 0.05))
        tot = up_p + down_p + flat_p

        return ExpertOutput(
            expert_name="SENTIMENT_EXPERT",
            available=True,
            confidence=0.65,
            directional_prob={"DOWN": round(down_p / tot, 4), "FLAT": round(flat_p / tot, 4), "UP": round(up_p / tot, 4)},
            expected_return_pct=round(signal * 0.2, 4),
            expected_volatility_pct=2.0,
            reasoning=f"NLP Sentiment={score:.3f}, Vel={vel:.3f}, UrgencyAlerts={getattr(sentiment_feat, 'high_urgency_alerts_count', 0)}"
        )

    @staticmethod
    def evaluate_macro_expert(macro_snap: Any, event_prox: Any) -> ExpertOutput:
        """Macro Expert: evaluates yield curve, rate environment, economic releases."""
        if not macro_snap or not event_prox:
            return ExpertOutput(
                expert_name="MACRO_EXPERT",
                available=False,
                confidence=0.0,
                directional_prob={"DOWN": 0.333, "FLAT": 0.334, "UP": 0.333},
                expected_return_pct=0.0,
                expected_volatility_pct=2.0,
                reasoning="Macro feeds unavailable"
            )

        m_regime = getattr(macro_snap, "macro_regime", "NEUTRAL")
        in_blackout = getattr(event_prox, "in_blackout_window", False)
        mult = getattr(event_prox, "event_risk_multiplier", 1.0)

        # Baseline macro directional stance
        signal = 0.1 if m_regime == "RISK_ON_EXPANSION" else (-0.15 if m_regime == "YIELD_CURVE_INVERSION_RISK" else 0.0)
        if in_blackout:
            conf = 0.2
        else:
            conf = 0.7

        up_p = float(np.clip(0.333 + signal * 0.3, 0.1, 0.8))
        down_p = float(np.clip(0.333 - signal * 0.3, 0.1, 0.8))
        flat_p = float(max(1.0 - up_p - down_p, 0.1))
        tot = up_p + down_p + flat_p

        return ExpertOutput(
            expert_name="MACRO_EXPERT",
            available=True,
            confidence=conf,
            directional_prob={"DOWN": round(down_p / tot, 4), "FLAT": round(flat_p / tot, 4), "UP": round(up_p / tot, 4)},
            expected_return_pct=round(signal * 0.15, 4),
            expected_volatility_pct=2.5 if in_blackout else 1.8,
            reasoning=f"Regime={m_regime}, InBlackout={in_blackout}, Multiplier={mult}"
        )

    @staticmethod
    def evaluate_onchain_expert(onchain_snap: Any) -> ExpertOutput:
        """On-Chain Expert: evaluates network activity, fee pressure, congestion."""
        if not onchain_snap or onchain_snap.status != "REAL":
            return ExpertOutput(
                expert_name="ONCHAIN_EXPERT",
                available=False,
                confidence=0.0,
                directional_prob={"DOWN": 0.333, "FLAT": 0.334, "UP": 0.333},
                expected_return_pct=0.0,
                expected_volatility_pct=2.0,
                reasoning="On-chain status not REAL or not configured"
            )

        # Elevated onchain fees indicate high economic activity/demand
        fee = getattr(onchain_snap, "fee_rate_standard", 1.0) or 1.0
        signal = 0.1 if fee > 10.0 else 0.0

        return ExpertOutput(
            expert_name="ONCHAIN_EXPERT",
            available=True,
            confidence=0.60,
            directional_prob={"DOWN": 0.30, "FLAT": 0.40, "UP": 0.30},
            expected_return_pct=0.05,
            expected_volatility_pct=1.9,
            reasoning=f"Chain={onchain_snap.chain}, Height={onchain_snap.block_height}, FeeStandard={fee}"
        )

    @staticmethod
    def evaluate_regime_expert(regime_state: Any) -> ExpertOutput:
        """Regime Expert: evaluates current market phase & stability."""
        if not regime_state:
            return ExpertOutput(
                expert_name="REGIME_EXPERT",
                available=False,
                confidence=0.0,
                directional_prob={"DOWN": 0.333, "FLAT": 0.334, "UP": 0.333},
                expected_return_pct=0.0,
                expected_volatility_pct=2.0,
                reasoning="Regime feeds unavailable"
            )

        reg = getattr(regime_state, "regime", "RANGE")
        probs = getattr(regime_state, "probabilities", {})

        signal = 0.0
        if reg in ["BULL_TREND", "EUPHORIA", "BREAKOUT"]:
            signal = 0.5
        elif reg in ["BEAR_TREND", "PANIC", "LIQUIDATION_CASCADE"]:
            signal = -0.5

        up_p = float(np.clip(0.333 + signal * 0.35, 0.05, 0.90))
        down_p = float(np.clip(0.333 - signal * 0.35, 0.05, 0.90))
        flat_p = float(max(1.0 - up_p - down_p, 0.05))
        tot = up_p + down_p + flat_p

        return ExpertOutput(
            expert_name="REGIME_EXPERT",
            available=True,
            confidence=round(getattr(regime_state, "regime_probability", 0.7), 3),
            directional_prob={"DOWN": round(down_p / tot, 4), "FLAT": round(flat_p / tot, 4), "UP": round(up_p / tot, 4)},
            expected_return_pct=round(signal * 0.35, 4),
            expected_volatility_pct=round(getattr(regime_state, "market_stress_index", 30.0) / 15.0, 2),
            reasoning=f"Regime={reg}, Stability={getattr(regime_state, 'regime_stability', 0.5):.2f}"
        )
