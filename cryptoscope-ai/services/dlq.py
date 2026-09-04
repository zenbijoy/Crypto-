"""
Production Dead Letter Queue (DLQ) Manager for CryptoScope AI.
Phase 4: Dead Letter Queue.
"""
from __future__ import annotations
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger("CryptoScope.DLQ")


class DeadLetterRecord(BaseModel):
    dlq_id: str
    original_payload: Dict[str, Any]
    failure_reason: str
    exception_type: str
    consumer: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    retry_count: int = 0
    trace_id: str = "none"
    stream_name: str = "unknown"
    status: str = "PENDING"  # PENDING, RETRIED, PURGED, RESOLVED


class DeadLetterQueue:
    """Manages failure isolation, forensic inspection, safe retries, and explicit purging."""

    def __init__(self, max_records: int = 5000):
        self.max_records = max_records
        self._records: Dict[str, DeadLetterRecord] = {}

    def capture_failure(
        self,
        stream_name: str,
        consumer: str,
        original_payload: Dict[str, Any],
        error: Exception,
        trace_id: str = "unknown",
        retry_count: int = 0
    ) -> DeadLetterRecord:
        now = datetime.now(timezone.utc)
        dlq_id = f"dlq_{int(now.timestamp() * 1000)}_{trace_id[:8]}"
        record = DeadLetterRecord(
            dlq_id=dlq_id,
            original_payload=original_payload,
            failure_reason=str(error),
            exception_type=type(error).__name__,
            consumer=consumer,
            timestamp=now,
            retry_count=retry_count,
            trace_id=trace_id,
            stream_name=stream_name,
            status="PENDING"
        )
        if len(self._records) >= self.max_records:
            # Evict oldest resolved or pending record
            oldest_key = next(iter(self._records))
            del self._records[oldest_key]
        self._records[dlq_id] = record
        logger.warning(
            f"[DLQ] Captured failure in stream '{stream_name}' by consumer '{consumer}': "
            f"{type(error).__name__} - {str(error)} (DLQ ID: {dlq_id})"
        )
        return record

    def inspect(self, limit: int = 50, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Inspect DLQ records with forensic details."""
        results = []
        for r in reversed(list(self._records.values())):
            if status_filter and r.status != status_filter:
                continue
            d = r.model_dump()
            d["timestamp"] = r.timestamp.isoformat()
            results.append(d)
            if len(results) >= limit:
                break
        return results

    def get_record(self, dlq_id: str) -> Optional[DeadLetterRecord]:
        return self._records.get(dlq_id)

    def mark_retried(self, dlq_id: str, success: bool, reason: str = "") -> bool:
        rec = self._records.get(dlq_id)
        if not rec:
            return False
        rec.retry_count += 1
        if success:
            rec.status = "RESOLVED"
            logger.info(f"[DLQ] Record {dlq_id} successfully reprocessed and marked RESOLVED")
        else:
            rec.status = "PENDING"
            rec.failure_reason = f"Retry failed: {reason}"
        return True

    def purge(self, confirm: bool = False, dlq_id: Optional[str] = None) -> Dict[str, Any]:
        """Purge records with explicit confirmation parameter."""
        if not confirm:
            raise ValueError("Explicit confirmation (confirm=True) is required to purge DLQ records")

        if dlq_id:
            if dlq_id in self._records:
                del self._records[dlq_id]
                return {"status": "PURGED", "count": 1, "target": dlq_id}
            return {"status": "NOT_FOUND", "count": 0, "target": dlq_id}

        count = len(self._records)
        self._records.clear()
        logger.info(f"[DLQ] Explicit purge executed. Removed {count} dead-letter records.")
        return {"status": "PURGED", "count": count, "target": "ALL"}

    def stats(self) -> Dict[str, Any]:
        total = len(self._records)
        pending = sum(1 for r in self._records.values() if r.status == "PENDING")
        resolved = sum(1 for r in self._records.values() if r.status == "RESOLVED")
        return {
            "total_records": total,
            "pending": pending,
            "resolved": resolved
        }


dlq_manager = DeadLetterQueue()
