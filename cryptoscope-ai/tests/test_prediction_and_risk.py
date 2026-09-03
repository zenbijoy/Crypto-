"""
Unit Tests for Probabilistic Prediction & Risk Circuit Breakers
Verifies fan chart quantiles (P10-P90), confidence decomposition, risk engine veto, and disclaimer.
"""
import unittest
from services.prediction import prediction_engine
from core.constants import DISCLAIMER_TEXT

class TestPredictionAndRisk(unittest.TestCase):
    def test_prediction_output_structure_and_quantiles(self):
        for asset in ["BTC", "ETH", "SOL", "DOGE"]:
            forecast = prediction_engine.generate_forecast(symbol=f"{asset}USDT")
            
            # Verify mandatory regulatory disclaimer
            self.assertEqual(forecast["disclaimer"], DISCLAIMER_TEXT)
            
            # Verify fan chart quantiles strictly monotonic: P10 <= P25 <= P50 <= P75 <= P90
            q = forecast["price_quantiles"]
            self.assertTrue(q["p10"] <= q["p25"] <= q["p50"] <= q["p75"] <= q["p90"])
            
            # Verify probabilistic directional sums
            p = forecast["direction_probabilities"]
            self.assertTrue(0.99 <= (p["p_up"] + p["p_down"] + p["p_sideways"]) <= 1.01)
            
            # Verify confidence score bounds (0-100)
            self.assertTrue(0 <= forecast["confidence"] <= 100)
            
            # Verify risk decision and signal
            self.assertIn(forecast["risk_decision"], ["ALLOW", "REDUCE", "REJECT"])
            self.assertIn(forecast["signal"], ["STRONG LONG", "LONG", "NEUTRAL / NO-TRADE", "SHORT", "STRONG SHORT"])

    def test_risk_engine_veto_low_quality_data(self):
        forecast = prediction_engine.generate_forecast(symbol="BTCUSDT", data_quality_score=70)
        # Should trigger risk veto due to sub-90 quality score
        self.assertEqual(forecast["risk_decision"], "REJECT")
        self.assertEqual(forecast["signal"], "NEUTRAL / NO-TRADE")

if __name__ == "__main__":
    unittest.main()
