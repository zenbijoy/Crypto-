"""
Unit Tests for Binance Provider Normalization (Phase 20 & 29)
"""
from datetime import datetime, timezone
import pytest
from core.enums import Provider, MarketType, ContractType
from providers.base import CanonicalInstrument, CanonicalTicker


def test_binance_instrument_normalization():
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
    assert inst.canonical_symbol == "BTCUSDT"
    assert inst.provider == Provider.BINANCE
    assert inst.market_type == MarketType.PERPETUAL


def test_binance_ticker_parsing():
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
        instrument_id="BINANCE:BTCUSDT:PERPETUAL",
        canonical_symbol="BTCUSDT",
        provider=Provider.BINANCE,
        last_price=float(raw_payload["lastPrice"]),
        bid_price=float(raw_payload["bidPrice"]),
        ask_price=float(raw_payload["askPrice"]),
        high_24h=float(raw_payload["highPrice"]),
        low_24h=float(raw_payload["lowPrice"]),
        volume_24h=float(raw_payload["volume"]),
        quote_volume_24h=float(raw_payload["quoteVolume"]),
        price_change_percent_24h=float(raw_payload["priceChangePercent"]),
        timestamp=datetime.fromtimestamp(raw_payload["closeTime"] / 1000.0, tz=timezone.utc)
    )

    assert ticker.last_price == 92450.50
    assert ticker.bid_price == 92450.00
    assert ticker.ask_price == 92451.00
    assert ticker.price_change_percent_24h == 1.34
