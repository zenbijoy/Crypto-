"""
Administrative Model & System Kill Switch.
Phase 46: Model Kill Switch.
"""
from __future__ import annotations
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set
from pydantic import BaseModel, Field

logger = logging.getLogger("CryptoScope.KillSwitch")


class KillSwitchState(BaseModel):
    global_predictions_disabled: bool = False
    disabled_models: Set[str] = Field(default_factory=set)
    disabled_assets: Set[str] = Field(default_factory=set)
    disabled_horizons: Set[str] = Field(default_factory=set)
    disabled_providers: Set[str] = Field(default_factory=set)


class ModelKillSwitch:
    """Administrative multi-tier kill switch capable of instantly disabling models, assets, horizons, or all predictions."""

    def __init__(self):
        self.state = KillSwitchState()
        self.audit_trail: List[Dict[str, Any]] = []

    def set_global_prediction_kill(self, disable: bool, operator: str, reason: str):
        self.state.global_predictions_disabled = disable
        self._record_audit("GLOBAL_PREDICTIONS", "ALL", disable, operator, reason)
        logger.critical(f"[KillSwitch] GLOBAL PREDICTIONS DISABLED={disable} by {operator} (Reason: {reason})")

    def disable_asset(self, asset: str, disable: bool, operator: str, reason: str):
        sym = asset.upper().replace("/", "")
        if disable:
            self.state.disabled_assets.add(sym)
        else:
            self.state.disabled_assets.discard(sym)
        self._record_audit("ASSET", sym, disable, operator, reason)

    def disable_model(self, model_id: str, disable: bool, operator: str, reason: str):
        if disable:
            self.state.disabled_models.add(model_id)
        else:
            self.state.disabled_models.discard(model_id)
        self._record_audit("MODEL", model_id, disable, operator, reason)

    def is_prediction_allowed(
        self,
        asset: str,
        horizon: str,
        model_id: Optional[str] = None
    ) -> tuple[bool, str]:
        if self.state.global_predictions_disabled:
            return False, "PREDICTIONS_DISABLED"

        sym = asset.upper().replace("/", "")
        if sym in self.state.disabled_assets:
            return False, f"ASSET_DISABLED:{sym}"

        if horizon.lower() in self.state.disabled_horizons:
            return False, f"HORIZON_DISABLED:{horizon}"

        if model_id and model_id in self.state.disabled_models:
            return False, f"MODEL_DISABLED:{model_id}"

        return True, "ACTIVE"

    def _record_audit(self, scope: str, target: str, disabled: bool, operator: str, reason: str):
        self.audit_trail.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "scope": scope,
            "target": target,
            "action": "DISABLED" if disabled else "REENABLED",
            "operator": operator,
            "reason": reason
        })


kill_switch = ModelKillSwitch()
