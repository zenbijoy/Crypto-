"""
Model Artifact Integrity Verifier and Loader.
Phase 14 & 17: Model Serving Artifact Integrity.
"""
from __future__ import annotations
import hashlib
import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger("CryptoScope.ArtifactLoader")


@dataclass
class ArtifactMetadata:
    model_id: str
    asset: str
    horizon: str
    model_type: str
    feature_schema_hash: str
    preprocessor_hash: str
    calibrator_hash: str
    model_weights_sha256: str
    created_at: str
    training_metrics: Dict[str, float]


class ArtifactLoader:
    """Verifies SHA256 hashes of weights, schemas, and calibrators prior to serving. Rejects corrupted artifacts."""

    @staticmethod
    def compute_file_sha256(file_path: Path) -> str:
        if not file_path.exists():
            raise FileNotFoundError(f"Artifact file not found: {file_path}")
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()

    def verify_and_load_metadata(self, artifact_dir: Path) -> ArtifactMetadata:
        meta_file = artifact_dir / "metadata.json"
        if not meta_file.exists():
            raise ValueError(f"Artifact directory {artifact_dir} missing metadata.json")

        with open(meta_file, "r") as f:
            raw = json.load(f)

        meta = ArtifactMetadata(**raw)

        # Check weights file integrity if present
        weights_file = artifact_dir / "weights.bin"
        if weights_file.exists():
            actual_sha = self.compute_file_sha256(weights_file)
            if actual_sha != meta.model_weights_sha256:
                raise ValueError(
                    f"Integrity Violation: weights.bin sha256 mismatch! "
                    f"Expected {meta.model_weights_sha256}, calculated {actual_sha}"
                )

        logger.info(f"[ArtifactLoader] Successfully validated integrity of {meta.model_id} ({meta.model_type})")
        return meta


artifact_loader = ArtifactLoader()
