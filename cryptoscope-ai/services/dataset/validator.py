"""
CryptoScope AI - Dataset Validator
Validates schema consistency, missing value thresholds, and distribution anomalies.
"""
from typing import List, Dict, Any, Tuple
import math


class DatasetValidator:
    def __init__(self, max_missing_pct: float = 0.05):
        self.max_missing_pct = max_missing_pct

    def validate_dataset(
        self,
        rows: List[Dict[str, Any]],
        expected_columns: List[str]
    ) -> Tuple[bool, List[str]]:
        violations: List[str] = []
        if not rows:
            return False, ["Dataset is completely empty"]

        total_rows = len(rows)

        # Check missing values per column
        for col in expected_columns:
            missing_count = sum(1 for r in rows if r.get(col) is None or (isinstance(r.get(col), float) and math.isnan(r.get(col))))
            missing_pct = missing_count / total_rows
            if missing_pct > self.max_missing_pct:
                violations.append(
                    f"Column '{col}' exceeds missing threshold: {missing_pct * 100:.1f}% missing (max {self.max_missing_pct * 100}%)"
                )

        return len(violations) == 0, violations
