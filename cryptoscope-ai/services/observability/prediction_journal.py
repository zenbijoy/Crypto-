"""
Live Prediction Journal with Delayed Label Resolution.
Phase 38 & 39: Prediction Journal & Label Resolver.
"""
from __future__ import annotations
import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger("CryptoScope.PredictionJournal")


class JournalEntry(BaseModel):
    prediction_id: str
    asset: str
    horizon: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    horizon_seconds: int
    model_version: str
    feature_schema_version: str
    feature_snapshot_hash: str
    probabilities: Dict[str, float]
    forecast_return: float
    uncertainty_score: float
    regime: str
    signal: str
    risk_decision: str  # ALLOW, DEGRADE, REJECT
    data_quality_status: str
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    actual_return: Optional[float] = None
    actual_direction: Optional[str] = None  # UP, DOWN, NEUTRAL
    actual_high: Optional[float] = None
    actual_low: Optional[float] = None
    mfe: Optional[float] = None  # Maximum Favorable Excursion
    mae: Optional[float] = None  # Maximum Adverse Excursion


class PredictionJournal:
    """Durably records all live inferences and securely resolves ground-truth labels once observable."""

    def __init__(self, max_entries: int = 10000):
        self.max_entries = max_entries
        self._entries: Dict[str, JournalEntry] = {}

    def log_prediction(
        self,
        prediction_id: str,
        asset: str,
        horizon: str,
        horizon_seconds: int,
        model_version: str,
        feature_schema_version: str,
        feature_snapshot_hash: str,
        probabilities: Dict[str, float],
        forecast_return: float,
        uncertainty_score: float,
        regime: str,
        signal: str,
        risk_decision: str,
        data_quality_status: str
    ) -> JournalEntry:
        entry = JournalEntry(
            prediction_id=prediction_id,
            asset=asset,
            horizon=horizon,
            horizon_seconds=horizon_seconds,
            model_version=model_version,
            feature_schema_version=feature_schema_version,
            feature_snapshot_hash=feature_snapshot_hash,
            probabilities=probabilities,
            forecast_return=forecast_return,
            uncertainty_score=uncertainty_score,
            regime=regime,
            signal=signal,
            risk_decision=risk_decision,
            data_quality_status=data_quality_status
        )
        if len(self._entries) >= self.max_entries:
            oldest_key = next(iter(self._entries))
            del self._entries[oldest_key]

        self._entries[prediction_id] = entry
        return entry

    def resolve_label(
        self,
        prediction_id: str,
        actual_return: float,
        actual_high: float,
        actual_low: float,
        mfe: float,
        mae: float,
        current_time: Optional[datetime] = None
    ) -> bool:
        entry = self._entries.get(prediction_id)
        if not entry:
            return False

        now = current_time or datetime.now(timezone.utc)
        elapsed = (now - entry.timestamp).total_seconds()

        # Invariant: Never resolve before outcome is observable
        if elapsed < entry.horizon_seconds:
            logger.warning(
                f"[PredictionJournal] Refusing premature resolution of {prediction_id}: "
                f"Elapsed {elapsed:.1f}s < Horizon {entry.horizon_seconds}s"
            )
            return False

        direction = "UP" if actual_return > 0.0005 else ("DOWN" if actual_return < -0.0005 else "NEUTRAL")
        entry.resolved = True
        entry.resolved_at = now
        entry.actual_return = round(actual_return, 6)
        entry.actual_direction = direction
        entry.actual_high = actual_high
        entry.actual_low = actual_low
        entry.mfe = mfe
        entry.mae = mae

        logger.info(f"[PredictionJournal] Resolved label for {prediction_id}: return={actual_return:.4f}, dir={direction}")
        return True

    def get_resolved_entries(self, asset: Optional[str] = None, horizon: Optional[str] = None) -> List[JournalEntry]:
        results = []
        for e in self._entries.values():
            if not e.resolved:
                continue
            if asset and e.asset != asset:
                continue
            if horizon and e.horizon != horizon:
                continue
            results.append(e)
        return results

    def stats(self) -> Dict[str, Any]:
        total = len(self._entries)
        resolved = sum(1 for e in self._entries.values() if e.resolved)
        return {
            "total_predictions_logged": total,
            "resolved_count": resolved,
            "unresolved_pending": total - resolved
        }


prediction_journal = PredictionJournal()
