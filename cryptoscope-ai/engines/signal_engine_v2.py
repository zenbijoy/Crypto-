"""
CryptoScope AI - Signal Engine V2
Deterministic Signal Generator enforcing cost hurdles, transaction friction,
uncertainty vetoes, and directional convictions.
Signals: STRONG_LONG, LONG, NO_TRADE, SHORT, STRONG_SHORT.
"""
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class ActionableSignal(BaseModel):
    canonical_symbol: str
    horizon: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    signal: str  # "STRONG_LONG", "LONG", "NO_TRADE", "SHORT", "STRONG_SHORT"
    actionable: bool
    direction: str  # "UP", "FLAT", "DOWN"
    conviction_score: float  # 0.0 to 100.0
    
    expected_return_pct: float
    total_cost_hurdle_pct: float
    net_alpha_pct: float
    
    recommended_leverage: float
    stop_loss_pct: float
    take_profit_pct: float
    
    rationale: str


class SignalEngineV2:
    def __init__(
        self,
        base_taker_fee_pct: float = 0.04,  # 4 bps taker
        min_cost_multiple: float = 1.4,
        max_uncertainty: float = 65.0
    ):
        self.taker_fee = base_taker_fee_pct
        self.min_cost_multiple = min_cost_multiple
        self.max_uncertainty = max_uncertainty

    def generate_signal(
        self,
        canonical_symbol: str,
        horizon: str,
        direction: str,
        direction_prob: float,
        expected_return_pct: float,
        expected_volatility_pct: float,
        spread_bps: float,
        slippage_bps: float,
        funding_rate: float,
        uncertainty_score: float,
        in_event_blackout: bool = False
    ) -> ActionableSignal:
        now = datetime.now(timezone.utc)
        
        # Total roundtrip cost hurdle (fee x2 + spread + slippage + funding)
        fee_rt = self.taker_fee * 2.0
        spread_pct = spread_bps / 100.0
        slippage_pct = slippage_bps / 100.0
        funding_cost = abs(funding_rate) * 100.0
        total_cost_hurdle = fee_rt + spread_pct + slippage_pct + funding_cost
        required_alpha = total_cost_hurdle * self.min_cost_multiple

        abs_ret = abs(expected_return_pct)
        net_alpha = abs_ret - total_cost_hurdle

        # VETO CONDITIONS
        if in_event_blackout:
            return ActionableSignal(
                canonical_symbol=canonical_symbol,
                horizon=horizon,
                timestamp=now,
                signal="NO_TRADE",
                actionable=False,
                direction="FLAT",
                conviction_score=0.0,
                expected_return_pct=expected_return_pct,
                total_cost_hurdle_pct=round(total_cost_hurdle, 4),
                net_alpha_pct=round(net_alpha, 4),
                recommended_leverage=1.0,
                stop_loss_pct=round(expected_volatility_pct, 2),
                take_profit_pct=round(expected_volatility_pct * 1.5, 2),
                rationale="Event Blackout Active: high-volatility event release window"
            )

        if uncertainty_score >= self.max_uncertainty:
            return ActionableSignal(
                canonical_symbol=canonical_symbol,
                horizon=horizon,
                timestamp=now,
                signal="NO_TRADE",
                actionable=False,
                direction="FLAT",
                conviction_score=0.0,
                expected_return_pct=expected_return_pct,
                total_cost_hurdle_pct=round(total_cost_hurdle, 4),
                net_alpha_pct=round(net_alpha, 4),
                recommended_leverage=1.0,
                stop_loss_pct=round(expected_volatility_pct, 2),
                take_profit_pct=round(expected_volatility_pct * 1.5, 2),
                rationale=f"Model Uncertainty ({uncertainty_score:.1f}) exceeds safety ceiling ({self.max_uncertainty:.1f})"
            )

        if abs_ret < required_alpha:
            return ActionableSignal(
                canonical_symbol=canonical_symbol,
                horizon=horizon,
                timestamp=now,
                signal="NO_TRADE",
                actionable=False,
                direction="FLAT",
                conviction_score=0.0,
                expected_return_pct=expected_return_pct,
                total_cost_hurdle_pct=round(total_cost_hurdle, 4),
                net_alpha_pct=round(net_alpha, 4),
                recommended_leverage=1.0,
                stop_loss_pct=round(expected_volatility_pct, 2),
                take_profit_pct=round(expected_volatility_pct * 1.5, 2),
                rationale=f"Expected return {abs_ret:.3f}% does not clear hurdle {required_alpha:.3f}% (costs {total_cost_hurdle:.3f}%)"
            )

        # Conviction score (0-100)
        prob_boost = max((direction_prob - 0.5) * 200.0, 0.0)
        ret_boost = min((abs_ret / required_alpha) * 30.0, 40.0)
        uncert_discount = (100.0 - uncertainty_score) * 0.3
        conviction = round(min(prob_boost * 0.4 + ret_boost + uncert_discount, 100.0), 1)

        # Signal tiering
        if direction == "UP":
            sig = "STRONG_LONG" if conviction >= 75.0 and direction_prob >= 0.60 else "LONG"
            lev = 3.0 if sig == "STRONG_LONG" else 2.0
        elif direction == "DOWN":
            sig = "STRONG_SHORT" if conviction >= 75.0 and direction_prob >= 0.60 else "SHORT"
            lev = 3.0 if sig == "STRONG_SHORT" else 2.0
        else:
            sig = "NO_TRADE"
            lev = 1.0

        # Dynamic Stop Loss & Take Profit based on volatility
        sl = round(max(expected_volatility_pct * 0.8, total_cost_hurdle * 1.5), 2)
        tp = round(sl * 1.6, 2)

        return ActionableSignal(
            canonical_symbol=canonical_symbol,
            horizon=horizon,
            timestamp=now,
            signal=sig,
            actionable=bool(sig != "NO_TRADE"),
            direction=direction,
            conviction_score=conviction,
            expected_return_pct=round(expected_return_pct, 4),
            total_cost_hurdle_pct=round(total_cost_hurdle, 4),
            net_alpha_pct=round(net_alpha, 4),
            recommended_leverage=lev,
            stop_loss_pct=sl,
            take_profit_pct=tp,
            rationale=f"Conviction {conviction}/100, Net Alpha +{net_alpha:.3f}%, Prob {direction_prob*100:.1f}%"
        )
