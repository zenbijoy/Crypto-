"""
Production Configuration Management with Versioning and Auditability.
Phase 62 & 63: Configuration Management & Auditability.
"""
from __future__ import annotations
import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

from services.observability.audit_logger import audit_logger

logger = logging.getLogger("CryptoScope.ConfigManager")


class OperationalConfig(BaseModel):
    version: str = "2.0.0"
    config_hash: str = ""
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    # Data Freshness & Quality
    max_orderbook_age_seconds: float = 5.0
    max_trades_age_seconds: float = 10.0
    max_clock_skew_seconds: float = 2.0

    # Risk & Abstention
    no_trade_confidence_threshold: float = 65.0
    min_conviction_score: float = 0.60
    max_hourly_drawdown_pct: float = 2.5
    circuit_breaker_enabled: bool = True

    # Execution & Sizing
    paper_starting_balance: float = 100_000.0
    max_leverage: float = 5.0
    maker_fee_bps: float = 2.0
    taker_fee_bps: float = 5.0

    # Canary & Rollout
    canary_percentage: float = 5.0


class ConfigManager:
    """Manages versioned configuration snapshots and computes tamper-evident SHA256 checksums."""

    def __init__(self):
        self._current_config = OperationalConfig()
        self._recompute_hash()

    def _recompute_hash(self):
        dump = self._current_config.model_dump()
        dump.pop("config_hash", None)
        dump.pop("updated_at", None)
        raw = json.dumps(dump, sort_keys=True)
        self._current_config.config_hash = hashlib.sha256(raw.encode()).hexdigest()[:16]

    def get_config(self) -> OperationalConfig:
        return self._current_config

    def update_config(self, updates: Dict[str, Any], actor: str, reason: str) -> OperationalConfig:
        old_state = self._current_config.model_dump()
        new_data = {**old_state, **updates}
        new_data["updated_at"] = datetime.now(timezone.utc).isoformat()

        # Version bump
        v_parts = self._current_config.version.split(".")
        v_parts[-1] = str(int(v_parts[-1]) + 1)
        new_data["version"] = ".".join(v_parts)

        new_config = OperationalConfig(**new_data)
        self._current_config = new_config
        self._recompute_hash()

        audit_logger.record_action(
            action="UPDATE_OPERATIONAL_CONFIG",
            actor=actor,
            old_state=old_state,
            new_state=self._current_config.model_dump(),
            reason=reason
        )

        logger.info(f"[ConfigManager] Configuration updated to v{self._current_config.version} by {actor}")
        return self._current_config


config_manager = ConfigManager()
