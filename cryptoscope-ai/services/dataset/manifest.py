"""
CryptoScope AI - Dataset Manifest & Versioning
Strict metadata tracking for machine learning datasets to guarantee provenance and auditability.
"""
from datetime import datetime, timezone
import hashlib
import json
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class DatasetManifest(BaseModel):
    dataset_name: str
    git_commit: str = "master"
    feature_schema_hash: str
    start_time: datetime
    end_time: datetime
    row_count: int
    hash_sha256: str
    feature_columns: List[str]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(
        cls,
        dataset_name: str,
        feature_columns: List[str],
        start_time: datetime,
        end_time: datetime,
        row_count: int,
        data_bytes: bytes,
        git_commit: str = "head"
    ) -> "DatasetManifest":
        schema_str = json.dumps(sorted(feature_columns))
        schema_hash = hashlib.sha256(schema_str.encode("utf-8")).hexdigest()
        data_hash = hashlib.sha256(data_bytes).hexdigest()

        return cls(
            dataset_name=dataset_name,
            git_commit=git_commit,
            feature_schema_hash=schema_hash,
            start_time=start_time,
            end_time=end_time,
            row_count=row_count,
            hash_sha256=data_hash,
            feature_columns=feature_columns
        )
