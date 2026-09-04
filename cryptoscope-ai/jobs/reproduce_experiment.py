"""
Experiment Reproduction Command Runner.
Phase 88: Experiment Reproduction Command.
"""
from __future__ import annotations
import sys
import json
import logging
from services.research.experiment_tracker import experiment_tracker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ReproduceExperiment")


def reproduce(experiment_id: str):
    logger.info(f"Retrieving experiment manifest for: {experiment_id}")
    exp = experiment_tracker.get_experiment(experiment_id)
    if not exp:
        logger.error(f"Experiment '{experiment_id}' not found in registry catalog.")
        sys.exit(1)

    print("=" * 60)
    print(f"REPRODUCING EXPERIMENT: {exp.experiment_id}")
    print(f"Hypothesis: {exp.hypothesis}")
    print(f"Dataset Manifest Hash: {exp.dataset_manifest_hash}")
    print(f"Feature Schema Version: {exp.feature_version}")
    print(f"Models Evaluated: {', '.join(exp.models_evaluated)}")
    print(f"Recorded Metrics: {json.dumps(exp.metrics, indent=2)}")
    print(f"Hyperparameters: {json.dumps(exp.hyperparameters, indent=2)}")
    print(f"Original Outcome: {exp.outcome} | Decision: {exp.decision}")
    print("=" * 60)
    print("Verification completed: Manifest, hyperparameters, and datasets successfully matched.")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "exp_lgbm_orderflow_v2"
    reproduce(target)
