"""
Live Probability Calibration Monitor & Reliability Statistics.
Phase 40: Calibration Monitor.
"""
from __future__ import annotations
import math
from collections import defaultdict
from typing import Any, Dict, List

from services.observability.prediction_journal import JournalEntry, prediction_journal


class CalibrationMonitor:
    """Tracks observed hit frequency across confidence bins: [0.5, 0.6), [0.6, 0.7), ..., [0.9, 1.0]."""

    def __init__(self):
        self.bins = [
            (0.5, 0.6),
            (0.6, 0.7),
            (0.7, 0.8),
            (0.8, 0.9),
            (0.9, 1.0)
        ]

    def compute_binned_calibration(self, entries: List[JournalEntry]) -> Dict[str, Any]:
        if not entries:
            return {"sample_size": 0, "bins": {}, "ece": 0.0}

        bin_data = {
            f"{low:.1f}-{high:.1f}": {"count": 0, "correct": 0, "mean_conf": 0.0, "observed_acc": 0.0}
            for (low, high) in self.bins
        }

        bin_conf_sums = defaultdict(float)

        for e in entries:
            p_up = e.probabilities.get("p_up", 0.33)
            p_down = e.probabilities.get("p_down", 0.33)

            pred_dir = "UP" if p_up >= p_down else "DOWN"
            conf = max(p_up, p_down)

            is_correct = (pred_dir == e.actual_direction)

            for (low, high) in self.bins:
                if low <= conf < high or (high == 1.0 and conf == 1.0):
                    bkey = f"{low:.1f}-{high:.1f}"
                    bin_data[bkey]["count"] += 1
                    if is_correct:
                        bin_data[bkey]["correct"] += 1
                    bin_conf_sums[bkey] += conf
                    break

        total_samples = len(entries)
        ece = 0.0

        for bkey, data in bin_data.items():
            cnt = data["count"]
            if cnt > 0:
                data["mean_conf"] = round(bin_conf_sums[bkey] / cnt, 4)
                data["observed_acc"] = round(data["correct"] / cnt, 4)
                ece += (cnt / total_samples) * abs(data["observed_acc"] - data["mean_conf"])

        return {
            "sample_size": total_samples,
            "bins": bin_data,
            "ece": round(ece, 4)
        }


calibration_monitor = CalibrationMonitor()
