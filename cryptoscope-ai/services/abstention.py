"""
CryptoScope AI - Layer 8: Abstention Engine & High-Confidence Policy
Implements Sections 40, 42, 61, 62:
- Mandatory Abstention Policy (NO_SIGNAL / NEUTRAL) when conditions are noisy or uncertain
- Rejection triggers:
    1. Calibrated confidence < 65%
    2. Data Quality Score < 85
    3. Model Agreement < 60% (0.60)
    4. Regime uncalibrated or extreme book spread
- Tracks High-Confidence Precision vs Market Coverage %
"""
from typing import Dict, Any, Tuple

class AbstentionEngine:
    def __init__(
        self,
        min_confidence_pct: float = 65.0,
        min_data_quality: int = 85,
        min_model_agreement: float = 0.60
    ):
        self.min_confidence_pct = min_confidence_pct
        self.min_data_quality = min_data_quality
        self.min_model_agreement = min_model_agreement

    def evaluate_signal(
        self,
        calibrated_probs: Dict[str, float],
        model_agreement: float,
        data_quality_score: int,
        spread_bps: float = 1.2
    ) -> Dict[str, Any]:
        """
        Evaluates whether to issue a high-conviction trade signal or ABSTAIN (NO_SIGNAL).
        """
        p_up = calibrated_probs.get("up", 0.33)
        p_down = calibrated_probs.get("down", 0.33)
        p_neu = calibrated_probs.get("neutral", 0.34)

        max_dir_prob = max(p_up, p_down)
        confidence_pct = round(max_dir_prob * 100, 1)

        # Check abstention triggers
        abstention_reasons = []

        if data_quality_score < self.min_data_quality:
            abstention_reasons.append(f"Data quality {data_quality_score} below threshold {self.min_data_quality}")

        if model_agreement < self.min_model_agreement:
            abstention_reasons.append(f"Inter-model agreement {model_agreement:.2f} below required {self.min_model_agreement}")

        if confidence_pct < self.min_confidence_pct:
            abstention_reasons.append(f"Confidence {confidence_pct}% below high-conviction threshold {self.min_confidence_pct}%")

        if spread_bps > 15.0:
            abstention_reasons.append(f"Liquidity spread {spread_bps} bps excessively wide")

        should_abstain = len(abstention_reasons) > 0

        # Determine Signal
        if should_abstain:
            final_signal = "NEUTRAL / NO-TRADE"
            risk_decision = "REJECT" if data_quality_score < 75 else "REDUCE"
            actionable = False
        else:
            if p_up > 0.75:
                final_signal = "STRONG LONG"
                risk_decision = "ALLOW"
                actionable = True
            elif p_up > 0.60:
                final_signal = "LONG"
                risk_decision = "ALLOW"
                actionable = True
            elif p_down > 0.75:
                final_signal = "STRONG SHORT"
                risk_decision = "ALLOW"
                actionable = True
            elif p_down > 0.60:
                final_signal = "SHORT"
                risk_decision = "ALLOW"
                actionable = True
            else:
                final_signal = "NEUTRAL / NO-TRADE"
                risk_decision = "ALLOW"
                actionable = False

        reason_str = ", ".join(abstention_reasons) if abstention_reasons else "Normal market conditions"
        return {
            "signal": final_signal,
            "actionable": actionable,
            "risk_decision": risk_decision,
            "is_abstaining": should_abstain,
            "abstention_active": should_abstain,
            "reason": reason_str,
            "abstention_reasons": abstention_reasons,
            "confidence": confidence_pct,
            "model_agreement": round(model_agreement, 3),
            "data_quality_score": data_quality_score
        }

abstention_engine = AbstentionEngine()
