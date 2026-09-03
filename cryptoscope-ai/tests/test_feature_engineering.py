"""
Unit Tests for Comprehensive Quantitative Feature Engineering Engine
Verifies returns, volatility, technical indicators, orderbook OBI, derivatives z-scores, BTC beta, and meme factor.
"""
import unittest
from services.feature_engine import feature_engine

class TestFeatureEngineering(unittest.TestCase):
    def test_feature_calculation_btc_and_doge(self):
        candles = [
            {"close": 67000.0 + i * 10.0, "high": 67100.0 + i * 10.0, "low": 66900.0 + i * 10.0, "volume_base": 150.0}
            for i in range(50)
        ]
        orderbook = {
            "mid_price": 67500.0,
            "spread_bps": 1.2,
            "microprice": 67501.0,
            "imbalance_10bps": 0.35
        }

        # BTC Feature Computation
        btc_features = feature_engine.compute_all_features("BTC", candles, orderbook)
        self.assertIn("price_features", btc_features)
        self.assertIn("technical_indicators", btc_features)
        self.assertIn("microstructure", btc_features)
        self.assertIn("derivatives", btc_features)
        self.assertGreater(btc_features["technical_indicators"]["rsi_14"], 0)
        self.assertEqual(btc_features["microstructure"]["spread_bps"], 1.2)

        # DOGE Feature Computation
        doge_candles = [
            {"close": 0.120 + i * 0.0001, "high": 0.122, "low": 0.119, "volume_base": 5000000.0}
            for i in range(50)
        ]
        doge_features = feature_engine.compute_all_features("DOGE", doge_candles, orderbook, btc_candles_1h=candles)
        self.assertEqual(doge_features["asset"], "DOGE")
        self.assertIn("meme_sector_factor", doge_features)
        # Truthful check: meme_sector_factor is None without real social/on-chain telemetry
        self.assertIsNone(doge_features["meme_sector_factor"])
        self.assertIsNotNone(doge_features["cross_asset_dynamics"]["btc_correlation_24h"])

    def test_zero_fabricated_fallbacks(self):
        from core.exceptions import DataUnavailableException
        with self.assertRaises(DataUnavailableException):
            feature_engine.compute_all_features("BTC", candles_1h=[])

if __name__ == "__main__":
    unittest.main()
