"""
CryptoScope AI - Dataset Leakage Checker
Enforces strict temporal ordering:
event_time <= available_time <= training_cutoff_time.
Flags and rejects any lookahead bias or future data leakage in training pipelines.
"""
from datetime import datetime
from typing import List, Dict, Any, Tuple
import logging

logger = logging.getLogger("cryptoscope.dataset.leakage")


class DataLeakageException(Exception):
    pass


class LeakageChecker:
    @staticmethod
    def verify_temporal_integrity(
        rows: List[Dict[str, Any]],
        training_cutoff_time: datetime,
        event_time_col: str = "event_time",
        available_time_col: str = "available_time"
    ) -> Tuple[bool, List[str]]:
        violations: List[str] = []

        for idx, row in enumerate(rows):
            ev_time = row.get(event_time_col)
            avail_time = row.get(available_time_col, ev_time)

            if ev_time is None:
                violations.append(f"Row {idx}: Missing {event_time_col}")
                continue

            # Check 1: event_time <= available_time
            if avail_time and ev_time > avail_time:
                violations.append(
                    f"Row {idx}: Future event! event_time ({ev_time}) > available_time ({avail_time})"
                )

            # Check 2: available_time <= training_cutoff_time
            if avail_time and avail_time > training_cutoff_time:
                violations.append(
                    f"Row {idx}: Leakage past cutoff! available_time ({avail_time}) > cutoff ({training_cutoff_time})"
                )

        is_valid = len(violations) == 0
        if not is_valid:
            logger.error("Dataset Leakage Violations Found: %d issues", len(violations))

        return is_valid, violations
