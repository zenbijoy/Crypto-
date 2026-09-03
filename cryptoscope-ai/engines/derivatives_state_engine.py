"""
CryptoScope AI - Derivatives State Engine
Combines Price changes, Open Interest delta, and Funding rates to classify
institutional positioning regimes:
- NEW_LONG_EXPANSION: Price UP, OI UP
- NEW_SHORT_EXPANSION: Price DOWN, OI UP
- SHORT_COVERING: Price UP, OI DOWN
- LONG_LIQUIDATION: Price DOWN, OI DOWN
- LEVERAGE_BUILDUP: Price FLAT, OI UP
- NEUTRAL: Low activity / balanced
"""
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class DerivativesMarketState(BaseModel):
    canonical_symbol: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    state: str  # NEW_LONG_EXPANSION, NEW_SHORT_EXPANSION, SHORT_COVERING, LONG_LIQUIDATION, LEVERAGE_BUILDUP, NEUTRAL
    state_confidence: float  # 0.0 to 100.0
    price_delta_pct: float
    oi_delta_pct: float
    funding_bias: str
    squeeze_risk: str  # HIGH_SHORT_SQUEEZE, HIGH_LONG_SQUEEZE, ELEVATED, LOW
    leverage_risk_score: float  # 0.0 to 100.0
    summary: str


class DerivativesStateEngine:
    def __init__(self, price_deadband_pct: float = 0.08, oi_deadband_pct: float = 0.15):
        self.price_deadband = price_deadband_pct
        self.oi_deadband = oi_deadband_pct

    def classify(
        self,
        canonical_symbol: str,
        price_delta_pct: float,
        oi_delta_pct: float,
        funding_rate: float,
        funding_z_score: float = 0.0
    ) -> DerivativesMarketState:
        # Determine price direction
        p_dir = 0
        if price_delta_pct > self.price_deadband:
            p_dir = 1
        elif price_delta_pct < -self.price_deadband:
            p_dir = -1

        # Determine OI direction
        oi_dir = 0
        if oi_delta_pct > self.oi_deadband:
            oi_dir = 1
        elif oi_delta_pct < -self.oi_deadband:
            oi_dir = -1

        # Institutional Regime
        if p_dir == 1 and oi_dir == 1:
            state = "NEW_LONG_EXPANSION"
            summary = "Aggressive long positioning entering; open interest expanding with price rally."
        elif p_dir == -1 and oi_dir == 1:
            state = "NEW_SHORT_EXPANSION"
            summary = "Aggressive short positioning entering; open interest expanding with price decline."
        elif p_dir == 1 and oi_dir == -1:
            state = "SHORT_COVERING"
            summary = "Short covering rally; positions closing, lower open interest supporting price bump."
        elif p_dir == -1 and oi_dir == -1:
            state = "LONG_LIQUIDATION"
            summary = "Long liquidation / deleveraging; forced closures driving market lower."
        elif p_dir == 0 and oi_dir == 1:
            state = "LEVERAGE_BUILDUP"
            summary = "Heavy leverage buildup in tight range; elevated risk of breakout or cascade."
        else:
            state = "NEUTRAL"
            summary = "Market in balanced or consolidating state with subdued positioning changes."

        # Confidence (proportional to magnitude)
        mag = min(abs(price_delta_pct) * 20.0 + abs(oi_delta_pct) * 15.0, 100.0)
        confidence = max(mag, 50.0) if state != "NEUTRAL" else 60.0

        # Squeeze Risk
        # Extreme negative funding + price stabilizing or rising = SHORT_SQUEEZE
        # Extreme positive funding + price stalling or falling = LONG_SQUEEZE
        if funding_rate < -0.0002 and (p_dir >= 0 or oi_dir == 1):
            squeeze_risk = "HIGH_SHORT_SQUEEZE"
            lev_score = 85.0
        elif funding_rate > 0.0003 and (p_dir <= 0 or oi_dir == 1):
            squeeze_risk = "HIGH_LONG_SQUEEZE"
            lev_score = 85.0
        elif state == "LEVERAGE_BUILDUP":
            squeeze_risk = "ELEVATED"
            lev_score = 70.0
        else:
            squeeze_risk = "LOW"
            lev_score = 25.0

        funding_bias = "BULLISH_EXPENSIVE" if funding_rate > 0.00015 else ("BEARISH_DISCOUNT" if funding_rate < -0.00005 else "NEUTRAL")

        return DerivativesMarketState(
            canonical_symbol=canonical_symbol,
            state=state,
            state_confidence=round(confidence, 1),
            price_delta_pct=round(price_delta_pct, 4),
            oi_delta_pct=round(oi_delta_pct, 4),
            funding_bias=funding_bias,
            squeeze_risk=squeeze_risk,
            leverage_risk_score=round(lev_score, 1),
            summary=summary
        )
