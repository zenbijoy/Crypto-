"""
CryptoScope AI - Dataset Builder
Builds point-in-time training and backtesting datasets with verified schema and zero lookahead leakage.
"""
from datetime import datetime, timezone
import json
from typing import List, Dict, Any, Optional, Tuple

from services.dataset.manifest import DatasetManifest
from services.dataset.leakage_check import LeakageChecker, DataLeakageException
from services.dataset.validator import DatasetValidator


class DatasetBuilder:
    def __init__(self, dataset_name: str):
        self.dataset_name = dataset_name
        self.validator = DatasetValidator()

    def build_dataset(
        self,
        raw_rows: List[Dict[str, Any]],
        feature_columns: List[str],
        cutoff_time: datetime
    ) -> Tuple[List[Dict[str, Any]], DatasetManifest]:
        # 1. Enforce temporal anti-leakage constraints
        is_leak_free, violations = LeakageChecker.verify_temporal_integrity(
            raw_rows, training_cutoff_time=cutoff_time
        )
        if not is_leak_free:
            raise DataLeakageException(f"Dataset build rejected due to temporal leakage: {violations[:5]}")

        # 2. Validate feature columns & missingness
        is_valid, val_violations = self.validator.validate_dataset(raw_rows, feature_columns)
        if not is_valid:
            raise ValueError(f"Dataset validation failed: {val_violations}")

        # 3. Compute timespan & manifest
        start_time = min(r["event_time"] for r in raw_rows)
        end_time = max(r["event_time"] for r in raw_rows)
        data_bytes = json.dumps(raw_rows, default=str).encode("utf-8")

        manifest = DatasetManifest.create(
            dataset_name=self.dataset_name,
            feature_columns=feature_columns,
            start_time=start_time,
            end_time=end_time,
            row_count=len(raw_rows),
            data_bytes=data_bytes
        )

        return raw_rows, manifest
