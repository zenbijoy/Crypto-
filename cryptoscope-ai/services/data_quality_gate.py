"""
Production Data Freshness SLOs and Data Quality Gate.
Phase 12 & 13: Data Freshness SLOs & Data Quality Gate.
"""
from __future__ import annotations
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class FreshnessStatus(str, Enum):
    LIVE = "LIVE"
    DEGRADED = "DEGRADED"
    STALE = "STALE"
    UNAVAILABLE = "UNAVAILABLE"


class GateDecision(str, Enum):
    ALLOW = "ALLOW"
    DEGRADE = "DEGRADE"
    REJECT = "REJECT"


@dataclass
class FreshnessSLOConfig:
    trade_feed_max_sec: float = 10.0
    book_ticker_max_sec: float = 3.0
    orderbook_max_sec: float = 5.0
    candle_1m_max_sec: float = 75.0
    funding_max_sec: float = 900.0
    open_interest_max_sec: float = 300.0
    macro_max_sec: float = 86400.0
    onchain_max_sec: float = 7200.0
    news_max_sec: float = 3600.0
    max_clock_skew_sec: float = 2.0


class DataQualityGate:
    """Evaluates features and data feeds prior to model inference. Rejection triggers NO_PREDICTION."""

    def __init__(self, config: Optional[FreshnessSLOConfig] = None):
        self.config = config or FreshnessSLOConfig()
        self.mandatory_features = [
            "spread_bps",
            "microprice",
            "order_imbalance",
            "realized_volatility_5m",
            "funding_rate"
        ]

    def evaluate_feature_freshness(self, feature_name: str, age_seconds: float) -> FreshnessStatus:
        if math.isinf(age_seconds) or math.isnan(age_seconds):
            return FreshnessStatus.UNAVAILABLE

        threshold = 60.0
        if "order" in feature_name or "spread" in feature_name or "microprice" in feature_name:
            threshold = self.config.orderbook_max_sec
        elif "volatility" in feature_name or "cvd" in feature_name:
            threshold = self.config.trade_feed_max_sec
        elif "funding" in feature_name or "basis" in feature_name:
            threshold = self.config.funding_max_sec
        elif "liquidation" in feature_name:
            threshold = 300.0

        if age_seconds <= threshold:
            return FreshnessStatus.LIVE
        elif age_seconds <= threshold * 2.5:
            return FreshnessStatus.DEGRADED
        else:
            return FreshnessStatus.STALE

    def check(
        self,
        features: Dict[str, float],
        availability_mask: Dict[str, bool],
        freshness_mask: Dict[str, float],
        clock_skew_seconds: float = 0.0,
        provider_healthy: bool = True
    ) -> Tuple[GateDecision, str, Dict[str, Any]]:
        """
        Evaluate full quality state.
        Returns (GateDecision, reason, metadata).
        """
        rejection_reasons = []
        degradation_reasons = []

        # 1. Provider Health Check
        if not provider_healthy:
            rejection_reasons.append("Primary exchange provider reported UNHEALTHY/OFFLINE")

        # 2. Clock Skew Check
        if abs(clock_skew_seconds) > self.config.max_clock_skew_sec:
            rejection_reasons.append(
                f"Clock skew ({clock_skew_seconds:.2f}s) exceeds safe threshold ({self.config.max_clock_skew_sec}s)"
            )

        # 3. Mandatory Features Presence & NaN/Inf Checks
        for req in self.mandatory_features:
            is_avail = availability_mask.get(req, False)
            val = features.get(req)
            if not is_avail or val is None or math.isnan(val) or math.isinf(val):
                rejection_reasons.append(f"Mandatory feature '{req}' is MISSING or NaN/Inf")

        # 4. Freshness SLO Evaluation
        freshness_states = {}
        for fname, age in freshness_mask.items():
            status = self.evaluate_feature_freshness(fname, age)
            freshness_states[fname] = status.value
            if fname in self.mandatory_features:
                if status == FreshnessStatus.STALE or status == FreshnessStatus.UNAVAILABLE:
                    rejection_reasons.append(f"Mandatory feature '{fname}' is {status.value} (age: {age:.1f}s)")
                elif status == FreshnessStatus.DEGRADED:
                    degradation_reasons.append(f"Mandatory feature '{fname}' is DEGRADED (age: {age:.1f}s)")
            else:
                # Optional feature
                if status in (FreshnessStatus.DEGRADED, FreshnessStatus.STALE):
                    degradation_reasons.append(f"Optional feature '{fname}' is {status.value}")

        # 5. Determine Overall Decision
        if rejection_reasons:
            decision = GateDecision.REJECT
            primary_reason = "; ".join(rejection_reasons)
        elif degradation_reasons:
            decision = GateDecision.DEGRADE
            primary_reason = "; ".join(degradation_reasons)
        else:
            decision = GateDecision.ALLOW
            primary_reason = "All quality and freshness criteria met"

        details = {
            "decision": decision.value,
            "rejection_reasons": rejection_reasons,
            "degradation_reasons": degradation_reasons,
            "freshness_states": freshness_states,
            "clock_skew_seconds": clock_skew_seconds,
            "evaluated_at": datetime.now(timezone.utc).isoformat()
        }

        return decision, primary_reason, details


data_quality_gate = DataQualityGate()
