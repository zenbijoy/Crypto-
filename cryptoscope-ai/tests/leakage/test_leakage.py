"""
CryptoScope AI - Mandatory Anti-Leakage Automated Test Suite
Implements Section 65: Leakage Test Suite
Ensures:
1. Scaler trained strictly on historical window
2. Chronology preserved in splits with positive embargo
3. No future observations accessed
"""
import unittest
from datetime import datetime, timezone, timedelta
from core.time import assert_point_in_time
from ml.preprocessing.scaler import LeakageFreeScaler
from ml.datasets.walk_forward import WalkForwardValidator

class TestAntiLeakage(unittest.TestCase):
    def test_point_in_time_integrity(self):
        now = datetime.now(timezone.utc)
        past = now - timedelta(minutes=15)
        future = now + timedelta(minutes=15)

        # Past data is valid
        assert_point_in_time(past, now)

        # Future data access MUST raise ValueError
        with self.assertRaises(ValueError):
            assert_point_in_time(future, now)

    def test_scaler_no_future_leakage(self):
        historical_data = [100.0, 102.0, 101.0, 103.0, 105.0]
        future_data = [150.0, 160.0]

        scaler = LeakageFreeScaler()
        scaler.fit(historical_data)

        # Scaler mean must match historical data only
        self.assertEqual(round(scaler.mean, 1), 102.2)
        
        transformed_future = scaler.transform(future_data)
        self.assertEqual(len(transformed_future), 2)

    def test_walk_forward_chronology_and_embargo(self):
        validator = WalkForwardValidator(train_window_size=500, val_window_size=100, embargo_size=20)
        splits = list(validator.split(1000))
        
        self.assertTrue(len(splits) > 0)
        for train_idx, embargo_idx, val_idx in splits:
            # Train strictly before Embargo and Val
            self.assertLess(max(train_idx), min(embargo_idx))
            self.assertLess(max(embargo_idx), min(val_idx))
            # Embargo distance respected
            self.assertGreaterEqual(min(val_idx) - max(train_idx), 20)

if __name__ == "__main__":
    unittest.main()
