"""
Unit Tests for CryptoScope AI Providers & Normalization Layer
Verifies Binance, Bybit, OKX, Coinbase, Hyperliquid adapters and canonical DTOs.
"""
import unittest
import asyncio
from providers.exchanges.binance import BinanceAdapter
from providers.exchanges.bybit import BybitAdapter
from providers.exchanges.additional import OKXAdapter, CoinbaseAdapter, HyperliquidAdapter
from providers.base import CanonicalTicker, CanonicalOrderBook
from core.enums import Provider

class TestProvidersAndNormalization(unittest.TestCase):
    def test_binance_discovery_and_normalization(self):
        adapter = BinanceAdapter()
        instruments = asyncio.run(adapter.discover_instruments())
        self.assertGreater(len(instruments), 0)
        
        # Check BTC and DOGE discovery
        btc_inst = next((i for i in instruments if i.base_asset == "BTC"), None)
        self.assertIsNotNone(btc_inst)
        self.assertEqual(btc_inst.provider, Provider.BINANCE)
        
        doge_inst = next((i for i in instruments if i.base_asset == "DOGE"), None)
        self.assertIsNotNone(doge_inst)
        self.assertTrue(doge_inst.is_memecoin)

        # Test Ticker
        ticker = asyncio.run(adapter.fetch_ticker(btc_inst))
        self.assertIsInstance(ticker, CanonicalTicker)
        self.assertGreater(ticker.price, 0)
        self.assertLessEqual(ticker.bid_price, ticker.ask_price)

        # Test OrderBook
        ob = asyncio.run(adapter.fetch_orderbook(btc_inst))
        self.assertIsInstance(ob, CanonicalOrderBook)
        self.assertGreater(len(ob.bids), 0)
        self.assertGreater(len(ob.asks), 0)
        self.assertGreaterEqual(ob.spread_bps, 0)

    def test_bybit_okx_hyperliquid_derivatives(self):
        bybit = BybitAdapter()
        okx = OKXAdapter()
        hl = HyperliquidAdapter()

        bybit_insts = asyncio.run(bybit.discover_instruments())
        okx_insts = asyncio.run(okx.discover_instruments())
        hl_insts = asyncio.run(hl.discover_instruments())

        self.assertGreater(len(bybit_insts), 0)
        self.assertGreater(len(okx_insts), 0)
        self.assertGreater(len(hl_insts), 0)

        # Test derivatives snapshot
        d_bybit = asyncio.run(bybit.fetch_derivatives_snapshot(bybit_insts[0]))
        d_okx = asyncio.run(okx.fetch_derivatives_snapshot(okx_insts[0]))
        d_hl = asyncio.run(hl.fetch_derivatives_snapshot(hl_insts[0]))

        self.assertIsNotNone(d_bybit.funding_rate)
        self.assertIsNotNone(d_okx.open_interest_usd)
        self.assertIsNotNone(d_hl.open_interest_usd)

if __name__ == "__main__":
    unittest.main()
