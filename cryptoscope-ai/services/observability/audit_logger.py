"""
Durable Audit Logging Service for Administrative and Operational Actions.
Phase 58: Audit Log.
"""
from __future__ import annotations
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger("CryptoScope.AuditLogger")


class AuditEvent(BaseModel):
    audit_id: str
    action: str
    actor: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    old_state: Dict[str, Any] = Field(default_factory=dict)
    new_state: Dict[str, Any] = Field(default_factory=dict)
    reason: str = ""
    ip_address: Optional[str] = None


class AuditLogger:
    """Durably logs administrative actions, model changes, and critical operational events."""

    def __init__(self, log_file: str = "./data/audit_log.jsonl"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self._in_memory_records: List[AuditEvent] = []

    def record_action(
        self,
        action: str,
        actor: str,
        old_state: Dict[str, Any],
        new_state: Dict[str, Any],
        reason: str = "",
        ip_address: Optional[str] = None
    ) -> AuditEvent:
        now = datetime.now(timezone.utc)
        audit_id = f"aud_{int(now.timestamp()*1000)}"
        event = AuditEvent(
            audit_id=audit_id,
            action=action,
            actor=actor,
            timestamp=now.isoformat(),
            old_state=old_state,
            new_state=new_state,
            reason=reason,
            ip_address=ip_address
        )

        self._in_memory_records.append(event)

        # Append to durable jsonl log
        try:
            with open(self.log_file, "a") as f:
                f.write(json.dumps(event.model_dump()) + "\n")
        except Exception as e:
            logger.error(f"[AuditLogger] Failed writing to audit file: {e}")

        logger.info(f"[AuditLogger] Logged '{action}' by '{actor}': {reason}")
        return event

    def query(self, limit: int = 50, action_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        results = []
        for ev in reversed(self._in_memory_records):
            if action_filter and ev.action != action_filter:
                continue
            results.append(ev.model_dump())
            if len(results) >= limit:
                break
        return results


audit_logger = AuditLogger()
