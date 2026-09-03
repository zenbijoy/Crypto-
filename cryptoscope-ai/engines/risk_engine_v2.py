"""
CryptoScope AI - Risk Engine V2 & Market Circuit Breakers
Deterministic risk veto logic enforcing market stability invariants,
feed freshness, orderbook health, and execution safety limits.
Veto Decisions: ALLOW, REDUCE, REJECT.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class CircuitBreakerStatus(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    all_clear: bool
    stale_feed_tripped: bool
    crossed_book_tripped: bool
    spread_anomaly_tripped: bool
    liquidation_cascade_tripped: bool
    active_reasons: List[str]


class RiskVetoDecision(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    decision: str  # "ALLOW", "REDUCE", "REJECT"
    allowed_position_fraction: float  # 0.0 to 1.0
    recommended_leverage: float
    circuit_breakers: CircuitBreakerStatus
    veto_reason: Optional[str] = None


class MarketCircuitBreakers:
    @staticmethod
    def evaluate(
        feed_age_seconds: float,
        best_bid: float,
        best_ask: float,
        max_venue_spread_bps: float,
        liquidation_pressure_score: float
    ) -> CircuitBreakerStatus:
        reasons = []
        stale = feed_age_seconds > 30.0
        crossed = (best_bid >= best_ask) and (best_bid > 0 and best_ask > 0)
        spread_disloc = max_venue_spread_bps > 35.0
        cascade = liquidation_pressure_score > 75.0

        if stale:
            reasons.append(f"Stale Feed: data age {feed_age_seconds:.1f}s > 30s threshold")
        if crossed:
            reasons.append(f"Crossed Orderbook: Bid {best_bid} >= Ask {best_ask}")
        if spread_disloc:
            reasons.append(f"Extreme Cross-Venue Dislocation: spread {max_venue_spread_bps:.1f}bps > 35bps")
        if cascade:
            reasons.append(f"Severe Liquidation Cascade: pressure score {liquidation_pressure_score:.1f} > 75")

        all_clear = not (stale or crossed or spread_disloc or cascade)

        return CircuitBreakerStatus(
            all_clear=all_clear,
            stale_feed_tripped=stale,
            crossed_book_tripped=crossed,
            spread_anomaly_tripped=spread_disloc,
            liquidation_cascade_tripped=cascade,
            active_reasons=reasons
        )


class RiskEngineV2:
    def __init__(self, max_daily_drawdown_pct: float = 3.5):
        self.max_daily_dd = max_daily_drawdown_pct

    def evaluate_risk(
        self,
        signal_actionable: bool,
        conviction_score: float,
        recommended_leverage: float,
        uncertainty_regime: str,
        circuit_status: CircuitBreakerStatus,
        current_daily_drawdown_pct: float = 0.0
    ) -> RiskVetoDecision:
        # Check Circuit Breakers first
        if not circuit_status.all_clear:
            return RiskVetoDecision(
                decision="REJECT",
                allowed_position_fraction=0.0,
                recommended_leverage=1.0,
                circuit_breakers=circuit_status,
                veto_reason="; ".join(circuit_status.active_reasons)
            )

        # Check Drawdown limit
        if current_daily_drawdown_pct >= self.max_daily_dd:
            return RiskVetoDecision(
                decision="REJECT",
                allowed_position_fraction=0.0,
                recommended_leverage=1.0,
                circuit_breakers=circuit_status,
                veto_reason=f"Daily drawdown {current_daily_drawdown_pct:.2f}% reached limit {self.max_daily_dd:.2f}%"
            )

        if not signal_actionable:
            return RiskVetoDecision(
                decision="REJECT",
                allowed_position_fraction=0.0,
                recommended_leverage=1.0,
                circuit_breakers=circuit_status,
                veto_reason="Signal is non-actionable (NO_TRADE)"
            )

        # Uncertainty Sizing Reductions
        if uncertainty_regime == "CRITICAL_ABSTAIN":
            return RiskVetoDecision(
                decision="REJECT",
                allowed_position_fraction=0.0,
                recommended_leverage=1.0,
                circuit_breakers=circuit_status,
                veto_reason="Critical model uncertainty abstain"
            )
        elif uncertainty_regime == "HIGH":
            # Scale down position by 50%
            return RiskVetoDecision(
                decision="REDUCE",
                allowed_position_fraction=0.5,
                recommended_leverage=min(recommended_leverage, 1.5),
                circuit_breakers=circuit_status,
                veto_reason="High uncertainty regime: position scaled to 50%"
            )
        elif uncertainty_regime == "MODERATE":
            return RiskVetoDecision(
                decision="ALLOW",
                allowed_position_fraction=0.8,
                recommended_leverage=recommended_leverage,
                circuit_breakers=circuit_status,
                veto_reason=None
            )
        else:
            return RiskVetoDecision(
                decision="ALLOW",
                allowed_position_fraction=1.0,
                recommended_leverage=recommended_leverage,
                circuit_breakers=circuit_status,
                veto_reason=None
            )
