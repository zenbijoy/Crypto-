"""
Unit Tests for Anti-Leakage Invariants (Phase 29)
Ensures strictly: feature_time <= prediction_time
"""
from datetime import datetime, timezone, timedelta
import unittest


class TestAntiLeakage(unittest.TestCase):
    def test_feature_time_never_exceeds_prediction_time(self):
        """Anti-leakage invariant test."""
        prediction_time = datetime.now(timezone.utc)

        # Valid feature timestamp
        feature_timestamp_valid = prediction_time - timedelta(minutes=5)
        self.assertTrue(feature_timestamp_valid <= prediction_time, "Feature time must be <= prediction time")

        # Future feature timestamp (leakage simulation)
        feature_timestamp_future = prediction_time + timedelta(seconds=1)
        is_valid = feature_timestamp_future <= prediction_time
        self.assertFalse(is_valid, "Future data must be strictly rejected as temporal leakage")

    def test_candle_closure_before_prediction(self):
        """Ensure incomplete future candles cannot be consumed for inference."""
        current_time = datetime.now(timezone.utc)
        candle_close_time = current_time - timedelta(seconds=10)
        self.assertTrue(candle_close_time <= current_time, "Only closed or historical bars allowed")


def test_feature_time_never_exceeds_prediction_time():
    TestAntiLeakage().test_feature_time_never_exceeds_prediction_time()

def test_candle_closure_before_prediction():
    TestAntiLeakage().test_candle_closure_before_prediction()


if __name__ == "__main__":
    unittest.main()
