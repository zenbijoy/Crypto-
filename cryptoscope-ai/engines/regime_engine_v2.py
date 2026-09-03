"""
CryptoScope AI - Market Regime Engine V2
Multi-factor probabilistic regime classifier incorporating price trends,
volatility, order flow imbalances, funding rates, open interest changes, and event proximity.
Outputs:
- 10 distinct regimes: BULL_TREND, BEAR_TREND, RANGE, HIGH_VOLATILITY, LOW_VOLATILITY, BREAKOUT, PANIC, EUPHORIA, LIQUIDATION_CASCADE, EVENT_RISK.
- regime_probability, regime_entropy, regime_stability.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import numpy as np


class MarketRegimeV2State(BaseModel):
    canonical_symbol: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    regime: str
    regime_probability: float  # probability of primary regime
    regime_entropy: float      # normalized entropy (0.0 = total certainty, 1.0 = maximum chaos)
    regime_stability: float    # 0.0 to 1.0 (persistence across recent intervals)
    
    probabilities: Dict[str, float]
    volatility_z_score: float
    trend_strength: float      # ADX / directional persistence proxy
    market_stress_index: float # 0.0 to 100.0


class MarketRegimeEngineV2:
    REGIMES = [
        "BULL_TREND", "BEAR_TREND", "RANGE",
        "HIGH_VOLATILITY", "LOW_VOLATILITY", "BREAKOUT",
        "PANIC", "EUPHORIA", "LIQUIDATION_CASCADE", "EVENT_RISK"
    ]

    def __init__(self, history_window: int = 20):
        self.history_window = history_window
        self._regime_history: List[str] = []

    def classify(
        self,
        canonical_symbol: str,
        price_return_pct: float,
        volatility_annualized: float,
        funding_rate: float,
        oi_delta_pct: float,
        order_imbalance: float,
        in_event_blackout: bool = False,
        liquidation_pressure: float = 0.0
    ) -> MarketRegimeV2State:
        # Construct raw logits for each regime
        logits = {r: 0.0 for r in self.REGIMES}

        # 1. EVENT_RISK
        if in_event_blackout:
            logits["EVENT_RISK"] += 5.0

        # 2. LIQUIDATION_CASCADE
        if liquidation_pressure > 60.0:
            logits["LIQUIDATION_CASCADE"] += 4.5 * (liquidation_pressure / 100.0)

        # 3. PANIC (Severe negative return + high vol)
        if price_return_pct < -2.0 and volatility_annualized > 60.0:
            logits["PANIC"] += 4.0

        # 4. EUPHORIA (Severe positive return + extreme positive funding)
        if price_return_pct > 2.0 and funding_rate > 0.0003:
            logits["EUPHORIA"] += 4.0

        # 5. BREAKOUT (Sharp move with expanding OI)
        if abs(price_return_pct) > 1.0 and oi_delta_pct > 1.5:
            logits["BREAKOUT"] += 3.5

        # 6. BULL_TREND
        if price_return_pct > 0.3 and order_imbalance > 0.1:
            logits["BULL_TREND"] += 2.5 + price_return_pct

        # 7. BEAR_TREND
        if price_return_pct < -0.3 and order_imbalance < -0.1:
            logits["BEAR_TREND"] += 2.5 + abs(price_return_pct)

        # 8. HIGH_VOLATILITY
        if volatility_annualized > 70.0:
            logits["HIGH_VOLATILITY"] += 3.0

        # 9. LOW_VOLATILITY
        if volatility_annualized < 30.0 and abs(price_return_pct) < 0.2:
            logits["LOW_VOLATILITY"] += 3.0

        # 10. RANGE (Baseline equilibrium)
        if abs(price_return_pct) < 0.3 and abs(order_imbalance) < 0.15:
            logits["RANGE"] += 2.2

        # Softmax normalization
        vals = np.array(list(logits.values()))
        exp_v = np.exp(vals - np.max(vals))
        probs_arr = exp_v / np.sum(exp_v)
        probs = {r: round(float(p), 4) for r, p in zip(self.REGIMES, probs_arr)}

        top_regime = max(probs, key=probs.get)
        top_prob = probs[top_regime]

        # Normalized Entropy: -sum(p * log(p)) / log(N)
        valid_p = probs_arr[probs_arr > 1e-9]
        entropy = -np.sum(valid_p * np.log(valid_p)) / np.log(len(self.REGIMES))

        # Stability tracking
        self._regime_history.append(top_regime)
        if len(self._regime_history) > self.history_window:
            self._regime_history.pop(0)

        stability = self._regime_history.count(top_regime) / len(self._regime_history)

        # Market stress index (0-100)
        stress = min((volatility_annualized / 80.0) * 40.0 + liquidation_pressure * 0.4 + (30.0 if top_regime in ["PANIC", "LIQUIDATION_CASCADE", "EVENT_RISK"] else 0.0), 100.0)

        return MarketRegimeV2State(
            canonical_symbol=canonical_symbol,
            regime=top_regime,
            regime_probability=round(top_prob, 3),
            regime_entropy=round(float(entropy), 3),
            regime_stability=round(stability, 3),
            probabilities=probs,
            volatility_z_score=round((volatility_annualized - 45.0) / 15.0, 2),
            trend_strength=round(min(abs(price_return_pct) * 25.0, 100.0), 1),
            market_stress_index=round(stress, 1)
        )
