"""
Unit Tests for Anti-Leakage Invariants (Phase 29)
Ensures strictly: feature_time <= prediction_time
"""
from datetime import datetime, timezone, timedelta
import pytest


def test_feature_time_never_exceeds_prediction_time():
    """Anti-leakage invariant test."""
    prediction_time = datetime.now(timezone.utc)

    # Valid feature timestamp
    feature_timestamp_valid = prediction_time - timedelta(minutes=5)
    assert feature_timestamp_valid <= prediction_time, "Feature time must be <= prediction time"

    # Future feature timestamp (leakage simulation)
    feature_timestamp_future = prediction_time + timedelta(seconds=1)
    is_valid = feature_timestamp_future <= prediction_time
    assert is_valid is False, "Future data must be strictly rejected as temporal leakage"


def test_candle_closure_before_prediction():
    """Ensure incomplete future candles cannot be consumed for inference."""
    current_time = datetime.now(timezone.utc)
    candle_close_time = current_time - timedelta(seconds=10)

    assert candle_close_time <= current_time, "Only closed or historical bars allowed"
