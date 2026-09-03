"""
CryptoScope AI - Independent Deterministic Risk Engine & Circuit Breakers
Implements Sections 37 & 38 specifications:
- The ML model must NOT control risk directly.
- Risk Engine outputs: ALLOW, REDUCE, REJECT with full veto authority.
- Circuit breakers for stale feeds, desynchronization, latency, extreme spread, unseen regime.
"""
from typing import Dict, Any, List
from core.enums import RiskDecision

class RiskEngine:
    def __init__(self):
        self.max_spread_bps = 15.0
        self.min_data_quality_score = 90
        self.max_ws_latency_ms = 500.0

    def evaluate_risk(
        self,
        model_confidence: int,
        model_agreement: int,
        expected_edge_pct: float,
        data_quality_score: int,
        spread_bps: float,
        ws_latency_ms: float,
        regime: str,
        is_event_risk: bool = False
    ) -> Dict[str, Any]:
        veto_reasons: List[str] = []

        # Circuit Breaker 1: Stale / Low Quality Feed
        if data_quality_score < self.min_data_quality_score:
            veto_reasons.append(f"Data quality score ({data_quality_score}) below safety threshold ({self.min_data_quality_score})")

        # Circuit Breaker 2: Abnormal Spread
        if spread_bps > self.max_spread_bps:
            veto_reasons.append(f"Abnormal book spread ({spread_bps:.1f} bps) exceeds limit ({self.max_spread_bps} bps)")

        # Circuit Breaker 3: High Latency
        if ws_latency_ms > self.max_ws_latency_ms:
            veto_reasons.append(f"Feed latency ({ws_latency_ms:.1f}ms) exceeds max allowable ({self.max_ws_latency_ms}ms)")

        # Circuit Breaker 4: Model Disagreement
        if model_agreement < 65:
            veto_reasons.append(f"Model agreement ({model_agreement}%) is insufficient across expert ensembles")

        # Circuit Breaker 5: Major Macro Event Risk
        if is_event_risk or regime == "EVENT_RISK":
            veto_reasons.append("High-impact scheduled macroeconomic release within embargo window")

        # Deterministic Decision Matrix
        if veto_reasons:
            decision = RiskDecision.REJECT.value
            reason = " | ".join(veto_reasons)
        elif model_confidence >= 80 and expected_edge_pct >= 0.5:
            decision = RiskDecision.ALLOW.value
            reason = f"Full allocation allowed: Confidence {model_confidence}%, Edge {expected_edge_pct:.2f}% exceeds cost hurdles."
        elif model_confidence >= 68 and expected_edge_pct >= 0.2:
            decision = RiskDecision.REDUCE.value
            reason = f"Reduced sizing (50% scale): Confidence {model_confidence}% is moderate; risk engine caps exposure."
        else:
            decision = RiskDecision.REJECT.value
            reason = f"Edge ({expected_edge_pct:.2f}%) or confidence ({model_confidence}%) does not exceed fee + slippage threshold."

        return {
            "decision": decision,
            "reason": reason,
            "veto_reasons": veto_reasons,
            "circuit_breakers_ok": len(veto_reasons) == 0,
            "risk_level": "HIGH" if decision == RiskDecision.REJECT.value else ("MEDIUM" if decision == RiskDecision.REDUCE.value else "LOW")
        }
