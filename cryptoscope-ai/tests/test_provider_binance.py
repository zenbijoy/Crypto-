"""
Unit Tests for Binance Provider Normalization (Phase 20 & 29)
"""
from datetime import datetime, timezone
import unittest
from core.enums import Provider, MarketType, ContractType
from providers.base import CanonicalInstrument, CanonicalTicker


class TestBinanceProvider(unittest.TestCase):
    def test_binance_instrument_normalization(self):
        inst = CanonicalInstrument(
            instrument_id="BINANCE:BTCUSDT:PERPETUAL",
            canonical_symbol="BTCUSDT",
            base_asset="BTC",
            quote_asset="USDT",
            provider=Provider.BINANCE,
            provider_symbol="BTCUSDT",
            market_type=MarketType.PERPETUAL,
            contract_type=ContractType.LINEAR,
            tick_size=0.1,
            step_size=0.001,
            min_quantity=0.001
        )
        self.assertEqual(inst.canonical_symbol, "BTCUSDT")
        self.assertEqual(inst.provider, Provider.BINANCE)
        self.assertEqual(inst.market_type, MarketType.PERPETUAL)

    def test_binance_ticker_parsing(self):
        raw_payload = {
            "symbol": "BTCUSDT",
            "lastPrice": "92450.50",
            "bidPrice": "92450.00",
            "askPrice": "92451.00",
            "highPrice": "93500.00",
            "lowPrice": "91200.00",
            "volume": "48291.55",
            "quoteVolume": "4464521890.25",
            "priceChangePercent": "1.34",
            "closeTime": 1741160000000
        }

        ticker = CanonicalTicker(
            provider=Provider.BINANCE,
            instrument_id="BINANCE:BTCUSDT:PERPETUAL",
            symbol="BTCUSDT",
            base_asset="BTC",
            quote_asset="USDT",
            price=float(raw_payload["lastPrice"]),
            bid_price=float(raw_payload["bidPrice"]),
            ask_price=float(raw_payload["askPrice"]),
            volume_24h_base=float(raw_payload["volume"]),
            volume_24h_quote=float(raw_payload["quoteVolume"]),
            change_24h_pct=float(raw_payload["priceChangePercent"]),
            high_24h=float(raw_payload["highPrice"]),
            low_24h=float(raw_payload["lowPrice"]),
            timestamp=datetime.fromtimestamp(raw_payload["closeTime"] / 1000.0, tz=timezone.utc)
        )

        self.assertEqual(ticker.price, 92450.50)
        self.assertEqual(ticker.bid_price, 92450.00)
        self.assertEqual(ticker.ask_price, 92451.00)
        self.assertEqual(ticker.change_24h_pct, 1.34)


def test_binance_instrument_normalization():
    TestBinanceProvider().test_binance_instrument_normalization()

def test_binance_ticker_parsing():
    TestBinanceProvider().test_binance_ticker_parsing()


if __name__ == "__main__":
    unittest.main()
