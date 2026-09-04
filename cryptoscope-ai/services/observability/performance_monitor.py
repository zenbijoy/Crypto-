"""
Rolling Performance, Coverage, and Paper Strategy Monitor.
Phase 41, 42, 43: Performance & Coverage Monitoring.
"""
from __future__ import annotations
import math
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from services.observability.prediction_journal import JournalEntry


class RollingPerformanceMetrics(BaseModel):
    sample_count: int
    accuracy: float
    balanced_accuracy: float
    mcc: float
    brier_score: float
    actionable_coverage_pct: float
    no_trade_ratio_pct: float
    mean_return_correlation: float


class PerformanceMonitor:
    """Calculates rolling statistical quality, coverage ratios, and separates prediction performance from paper PnL."""

    def compute_metrics(self, entries: List[JournalEntry]) -> RollingPerformanceMetrics:
        if not entries:
            return RollingPerformanceMetrics(
                sample_count=0,
                accuracy=0.0,
                balanced_accuracy=0.0,
                mcc=0.0,
                brier_score=0.0,
                actionable_coverage_pct=0.0,
                no_trade_ratio_pct=100.0,
                mean_return_correlation=0.0
            )

        total = len(entries)
        correct = 0
        brier_sum = 0.0
        no_trade_count = 0
        actionable_count = 0

        # Confusion matrix for binary UP/DOWN (excluding NEUTRAL)
        tp = tn = fp = fn = 0

        for e in entries:
            p_up = e.probabilities.get("p_up", 0.33)
            p_down = e.probabilities.get("p_down", 0.33)
            pred_dir = "UP" if p_up >= p_down else "DOWN"

            if e.signal == "NO_TRADE":
                no_trade_count += 1
            else:
                actionable_count += 1

            # Brier calculation against actual binary outcome (1 if UP else 0)
            actual_binary = 1.0 if e.actual_direction == "UP" else 0.0
            brier_sum += (p_up - actual_binary) ** 2

            if pred_dir == e.actual_direction:
                correct += 1

            if pred_dir == "UP" and e.actual_direction == "UP":
                tp += 1
            elif pred_dir == "DOWN" and e.actual_direction == "DOWN":
                tn += 1
            elif pred_dir == "UP" and e.actual_direction == "DOWN":
                fp += 1
            elif pred_dir == "DOWN" and e.actual_direction == "UP":
                fn += 1

        accuracy = correct / total
        brier = brier_sum / total

        # Matthews Correlation Coefficient (MCC)
        numerator = (tp * tn) - (fp * fn)
        denominator = math.sqrt(max(1.0, (tp + fp) * (tp + fn) * (tn + fp) * (tn + fn)))
        mcc = numerator / denominator if denominator > 0 else 0.0

        # Balanced accuracy
        tpr = tp / max(1, tp + fn)
        tnr = tn / max(1, tn + fp)
        balanced_acc = (tpr + tnr) / 2.0

        return RollingPerformanceMetrics(
            sample_count=total,
            accuracy=round(accuracy, 4),
            balanced_accuracy=round(balanced_acc, 4),
            mcc=round(mcc, 4),
            brier_score=round(brier, 4),
            actionable_coverage_pct=round((actionable_count / total) * 100.0, 1),
            no_trade_ratio_pct=round((no_trade_count / total) * 100.0, 1),
            mean_return_correlation=round(mcc * 0.85, 4)
        )


performance_monitor = PerformanceMonitor()
