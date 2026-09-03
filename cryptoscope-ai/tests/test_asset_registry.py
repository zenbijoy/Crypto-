"""
Unit Tests for Asset & Instrument Registry
Verifies Tier-1 (BTC, ETH, SOL, DOGE) deep coverage, Tier-2/3 discovery, and Model Readiness scores.
"""
import unittest
import asyncio
from services.registry import registry
from core.enums import AssetTier

class TestAssetRegistry(unittest.TestCase):
    def test_asset_discovery_and_tiering(self):
        count = asyncio.run(registry.initialize_and_discover())
        self.assertGreater(count, 0)
        
        # Check Tier-1 coverage for all 4 primary assets
        self.assertEqual(registry.get_tier("BTC"), AssetTier.TIER_1)
        self.assertEqual(registry.get_tier("ETH"), AssetTier.TIER_1)
        self.assertEqual(registry.get_tier("SOL"), AssetTier.TIER_1)
        self.assertEqual(registry.get_tier("DOGE"), AssetTier.TIER_1)
        
        # Check Tier-2
        self.assertEqual(registry.get_tier("BNB"), AssetTier.TIER_2)
        self.assertEqual(registry.get_tier("SUI"), AssetTier.TIER_2)

        # Check Tier-3
        self.assertEqual(registry.get_tier("RANDOM_UNKNOWN_TOKEN"), AssetTier.TIER_3)

        # Check Model Readiness Scores
        btc_readiness = registry.calculate_model_readiness("BTC")
        self.assertGreaterEqual(btc_readiness["score"], 90)
        self.assertEqual(btc_readiness["status"], "PRODUCTION_READY")

        doge_readiness = registry.calculate_model_readiness("DOGE")
        self.assertGreaterEqual(doge_readiness["score"], 90)
        self.assertEqual(doge_readiness["status"], "PRODUCTION_READY")

        all_assets = registry.list_all_assets()
        self.assertGreaterEqual(len(all_assets), 4)
        # Ensure Tier-1 assets are at the top of the list
        self.assertEqual(all_assets[0]["tier"], "TIER_1")

if __name__ == "__main__":
    unittest.main()
