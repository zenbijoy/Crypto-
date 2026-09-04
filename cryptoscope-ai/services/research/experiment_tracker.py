"""
Research Experiment Tracker & Reproducibility Catalog.
Phase 87 & 88: Experiment Tracker & Reproduction.
"""
from __future__ import annotations
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger("CryptoScope.ExperimentTracker")


class ExperimentRecord(BaseModel):
    experiment_id: str
    hypothesis: str
    dataset_manifest_hash: str
    feature_version: str
    models_evaluated: List[str]
    metrics: Dict[str, float]
    outcome: str  # SUCCESS, FAILED_HYPOTHESIS, INCONCLUSIVE
    decision: str  # REJECT, PROMOTE_TO_CANDIDATE, ARCHIVE
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    hyperparameters: Dict[str, Any] = Field(default_factory=dict)


class ExperimentTracker:
    """Durably tracks every research experiment, hypothesis, dataset checksum, and decision."""

    def __init__(self, storage_file: str = "./data/experiments.json"):
        self.storage_file = Path(storage_file)
        self.storage_file.parent.mkdir(parents=True, exist_ok=True)
        self._experiments: Dict[str, ExperimentRecord] = {}
        self._load()

    def _load(self):
        if self.storage_file.exists():
            try:
                with open(self.storage_file, "r") as f:
                    data = json.load(f)
                    for exp_id, record in data.items():
                        self._experiments[exp_id] = ExperimentRecord(**record)
            except Exception as e:
                logger.error(f"[ExperimentTracker] Error loading experiments: {e}")

    def _save(self):
        try:
            with open(self.storage_file, "w") as f:
                json.dump({k: v.model_dump() for k, v in self._experiments.items()}, f, indent=2)
        except Exception as e:
            logger.error(f"[ExperimentTracker] Error saving experiments: {e}")

    def log_experiment(
        self,
        experiment_id: str,
        hypothesis: str,
        dataset_manifest_hash: str,
        feature_version: str,
        models_evaluated: List[str],
        metrics: Dict[str, float],
        outcome: str,
        decision: str,
        hyperparameters: Optional[Dict[str, Any]] = None
    ) -> ExperimentRecord:
        record = ExperimentRecord(
            experiment_id=experiment_id,
            hypothesis=hypothesis,
            dataset_manifest_hash=dataset_manifest_hash,
            feature_version=feature_version,
            models_evaluated=models_evaluated,
            metrics=metrics,
            outcome=outcome,
            decision=decision,
            hyperparameters=hyperparameters or {}
        )
        self._experiments[experiment_id] = record
        self._save()
        logger.info(f"[ExperimentTracker] Logged experiment {experiment_id}: outcome={outcome}, decision={decision}")
        return record

    def get_experiment(self, experiment_id: str) -> Optional[ExperimentRecord]:
        return self._experiments.get(experiment_id)


experiment_tracker = ExperimentTracker()
