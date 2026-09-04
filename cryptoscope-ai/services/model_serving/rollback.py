"""
Production Model Rollback Controller.
Phase 23: Rollback Controller.
"""
from __future__ import annotations
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from services.model_serving.model_cache import model_cache

logger = logging.getLogger("CryptoScope.Rollback")


class RollbackRecord(BaseModel):
    rollback_id: str
    asset: str
    horizon: str
    previous_champion: str
    restored_champion: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    reason: str
    restored_schema_version: str = "v2.0"
    operator: str = "ADMIN"


class RollbackManager:
    """Manages one-command/API-safe model rollback restoring model, calibrator, thresholds, and schema."""

    def __init__(self):
        # (asset, horizon) -> list of previous champion version strings
        self._history: Dict[str, List[str]] = {}
        self.audit_log: List[RollbackRecord] = []

    def record_deployment(self, asset: str, horizon: str, version: str):
        key = f"{asset.upper().replace('/', '')}:{horizon}"
        if key not in self._history:
            self._history[key] = []
        self._history[key].append(version)

    async def rollback(
        self,
        asset: str,
        horizon: str,
        reason: str,
        operator: str = "ADMIN",
        target_version: Optional[str] = None
    ) -> Dict[str, Any]:
        key = f"{asset.upper().replace('/', '')}:{horizon}"
        curr_champ = model_cache.get_champion(asset, horizon)
        curr_id = curr_champ.model_id if curr_champ else "UNKNOWN"

        history = self._history.get(key, [])
        if not target_version:
            if len(history) < 2:
                raise ValueError(f"No previous champion in history for {key} to roll back to")
            target_version = history[-2]

        target_container = model_cache.get_model(asset, horizon, target_version)
        if not target_container:
            raise ValueError(f"Target rollback model version {target_version} not found in model pool")

        # Execute atomic swap back to previous champion
        success = await model_cache.atomic_swap_champion(
            asset=asset,
            horizon=horizon,
            new_version=target_version,
            candidate_model_obj=target_container.model,
            metadata=target_container.metadata
        )

        if not success:
            raise RuntimeError(f"Rollback to {target_version} failed during hot swap validation")

        rec = RollbackRecord(
            rollback_id=f"rb_{int(datetime.now(timezone.utc).timestamp())}",
            asset=asset,
            horizon=horizon,
            previous_champion=curr_id,
            restored_champion=target_container.model_id,
            reason=reason,
            operator=operator
        )
        self.audit_log.append(rec)
        logger.warning(
            f"[RollbackManager] Executed emergency rollback for {key}: "
            f"Restored {rec.restored_champion} (Reason: {reason})"
        )
        return rec.model_dump()


rollback_manager = RollbackManager()
