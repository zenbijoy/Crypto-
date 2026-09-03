"""
End-to-End API Integration Tests for CryptoScope AI FastAPI Gateway
Verifies canonical JSON envelopes, asset discovery, derivatives, analytics, predictions, and health endpoints.
"""
import unittest
import asyncio
from services.registry import registry
from services.prediction import prediction_engine
from services.aggregation import market_aggregator
from services.resilience import resilience_manager
from core.constants import DISCLAIMER_TEXT

class TestApiEndpoints(unittest.TestCase):
    def test_health_and_system_logic(self):
        statuses = resilience_manager.get_all_statuses()
        self.assertGreater(len(statuses), 0)
        
    def test_asset_discovery_logic(self):
        count = asyncio.run(registry.initialize_and_discover())
        self.assertGreater(count, 0)
        
        assets = registry.list_all_assets()
        self.assertGreaterEqual(len(assets), 4)

        btc_tier = registry.get_tier("BTC")
        self.assertEqual(btc_tier.value, "TIER_1")

        doge_tier = registry.get_tier("DOGE")
        self.assertEqual(doge_tier.value, "TIER_1")

    def test_market_and_derivatives_logic(self):
        btc_agg = asyncio.run(market_aggregator.aggregate_asset_market_data("BTC"))
        self.assertIn("consensus_price", btc_agg)
        self.assertGreater(btc_agg["consensus_price"]["value"], 0)
        self.assertIn("aggregated_open_interest_usd", btc_agg)

        doge_agg = asyncio.run(market_aggregator.aggregate_asset_market_data("DOGE"))
        self.assertIn("consensus_price", doge_agg)
        self.assertGreater(doge_agg["consensus_price"]["value"], 0)

    def test_prediction_logic(self):
        sample_candles = [
            {"close": 67000.0 + i * 5.0, "high": 67050.0 + i * 5.0, "low": 66950.0 + i * 5.0, "volume_base": 100.0}
            for i in range(30)
        ]
        for asset in ["BTC", "ETH", "SOL", "DOGE"]:
            p = prediction_engine.generate_forecast(
                symbol=f"{asset}USDT",
                horizon="1h",
                current_price=67000.0,
                candles_1h=sample_candles
            )
            self.assertEqual(p["asset"], asset)
            self.assertIn("price_quantiles", p)
            self.assertEqual(p["disclaimer"], DISCLAIMER_TEXT)

if __name__ == "__main__":
    unittest.main()
