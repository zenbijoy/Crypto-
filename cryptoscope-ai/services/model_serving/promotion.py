"""
Multi-Criteria Model Promotion Policy and Human Approval Gate.
Phase 21 & 22: Promotion Policy & Human Gate.
"""
from __future__ import annotations
import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger("CryptoScope.PromotionGate")


class LifecycleStage(str, Enum):
    EXPERIMENTAL = "EXPERIMENTAL"
    CANDIDATE = "CANDIDATE"
    SHADOW = "SHADOW"
    PAPER = "PAPER"
    PRODUCTION = "PRODUCTION"


class PromotionCriteria(BaseModel):
    min_sample_size: int = 200
    max_brier_score: float = 0.22
    min_mcc: float = 0.08
    max_ece: float = 0.07
    min_expectancy_bps: float = 2.0
    max_latency_p95_ms: float = 50.0
    min_shadow_days: float = 3.0


class PromotionAuditRecord(BaseModel):
    audit_id: str
    model_id: str
    from_stage: LifecycleStage
    to_stage: LifecycleStage
    approved_by: str
    decision: str  # APPROVED, REJECTED
    criteria_evaluation: Dict[str, Any]
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    reason: str = ""


class ModelPromotionManager:
    """Enforces multi-criteria verification and mandatory human approval for PRODUCTION promotions."""

    def __init__(self, criteria: Optional[PromotionCriteria] = None):
        self.criteria = criteria or PromotionCriteria()
        self.audit_log: List[PromotionAuditRecord] = []

    def evaluate_candidate(
        self,
        metrics: Dict[str, float],
        shadow_days: float,
        sample_count: int
    ) -> Dict[str, Any]:
        passed_checks = {}
        failed_checks = {}

        # 1. Sample size
        if sample_count >= self.criteria.min_sample_size:
            passed_checks["sample_size"] = f"{sample_count} >= {self.criteria.min_sample_size}"
        else:
            failed_checks["sample_size"] = f"{sample_count} < {self.criteria.min_sample_size}"

        # 2. Brier score
        brier = metrics.get("brier", 1.0)
        if brier <= self.criteria.max_brier_score:
            passed_checks["brier"] = f"{brier:.4f} <= {self.criteria.max_brier_score}"
        else:
            failed_checks["brier"] = f"{brier:.4f} > {self.criteria.max_brier_score}"

        # 3. MCC
        mcc = metrics.get("mcc", 0.0)
        if mcc >= self.criteria.min_mcc:
            passed_checks["mcc"] = f"{mcc:.4f} >= {self.criteria.min_mcc}"
        else:
            failed_checks["mcc"] = f"{mcc:.4f} < {self.criteria.min_mcc}"

        # 4. ECE
        ece = metrics.get("ece", 1.0)
        if ece <= self.criteria.max_ece:
            passed_checks["ece"] = f"{ece:.4f} <= {self.criteria.max_ece}"
        else:
            failed_checks["ece"] = f"{ece:.4f} > {self.criteria.max_ece}"

        # 5. Expectancy
        exp = metrics.get("expectancy_bps", 0.0)
        if exp >= self.criteria.min_expectancy_bps:
            passed_checks["expectancy"] = f"{exp:.1f}bps >= {self.criteria.min_expectancy_bps}bps"
        else:
            failed_checks["expectancy"] = f"{exp:.1f}bps < {self.criteria.min_expectancy_bps}bps"

        # 6. Shadow period
        if shadow_days >= self.criteria.min_shadow_days:
            passed_checks["shadow_days"] = f"{shadow_days:.1f}d >= {self.criteria.min_shadow_days}d"
        else:
            failed_checks["shadow_days"] = f"{shadow_days:.1f}d < {self.criteria.min_shadow_days}d"

        eligible = len(failed_checks) == 0
        return {
            "eligible": eligible,
            "passed_checks": passed_checks,
            "failed_checks": failed_checks
        }

    def request_promotion(
        self,
        model_id: str,
        from_stage: LifecycleStage,
        to_stage: LifecycleStage,
        evaluation: Dict[str, Any],
        approver: Optional[str] = None,
        reason: str = ""
    ) -> Dict[str, Any]:
        """Execute stage progression. Promotion to PRODUCTION strictly requires human approval."""
        if to_stage == LifecycleStage.PRODUCTION:
            if not approver or any(w in approver.lower() for w in ("system", "auto", "cron")):
                raise PermissionError(
                    "AUTOMATIC PRODUCTION PROMOTION IS DISABLED. "
                    "Promotion from PAPER to PRODUCTION strictly requires explicit Human Approval with valid auditor identity."
                )

        decision = "APPROVED" if evaluation.get("eligible", False) else "REJECTED"
        rec = PromotionAuditRecord(
            audit_id=f"prom_{int(datetime.now(timezone.utc).timestamp())}",
            model_id=model_id,
            from_stage=from_stage,
            to_stage=to_stage,
            approved_by=approver or "SYSTEM_PIPELINE",
            decision=decision,
            criteria_evaluation=evaluation,
            reason=reason
        )
        self.audit_log.append(rec)
        logger.info(f"[PromotionManager] {rec.decision} promotion of {model_id} to {to_stage.value} by {rec.approved_by}")
        return rec.model_dump()


promotion_manager = ModelPromotionManager()
