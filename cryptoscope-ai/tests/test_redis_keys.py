"""
Unit Tests for Redis Key Contracts and Financial Cache Envelopes (Phase 11 & 29)
Tests key formats and envelope structure in zero-dependency isolated mode.
"""
import unittest
import time
import json
from datetime import datetime, timezone


class RedisKeyContract:
    @staticmethod
    def key_ticker(provider: str, symbol: str) -> str:
        return f"ticker:{provider.lower()}:{symbol.upper()}"

    @staticmethod
    def key_funding(provider: str, symbol: str) -> str:
        return f"funding:{provider.lower()}:{symbol.upper()}"

    @staticmethod
    def key_oi(provider: str, symbol: str) -> str:
        return f"oi:{provider.lower()}:{symbol.upper()}"

    @staticmethod
    def key_orderbook(provider: str, symbol: str) -> str:
        return f"orderbook:{provider.lower()}:{symbol.upper()}"

    @staticmethod
    def key_feature(symbol: str, horizon: str, version: str = "v1") -> str:
        return f"feature:{symbol.upper()}:{horizon.lower()}:{version.lower()}"

    @staticmethod
    def key_prediction(symbol: str, horizon: str) -> str:
        return f"prediction:{symbol.upper()}:{horizon.lower()}"

    @staticmethod
    def key_provider_health(provider: str) -> str:
        return f"provider:health:{provider.lower()}"

    @staticmethod
    def format_financial_envelope(data: dict, source: str, ttl_seconds: int) -> dict:
        now = time.time()
        now_iso = datetime.now(timezone.utc).isoformat()
        return {
            "payload": data,
            "source": source,
            "updated_at": now_iso,
            "written_epoch": now,
            "ttl": ttl_seconds,
            "freshness": 0.0
        }


class TestRedisKeys(unittest.TestCase):
    def test_key_generators(self):
        c = RedisKeyContract
        self.assertEqual(c.key_ticker("binance", "btcusdt"), "ticker:binance:BTCUSDT")
        self.assertEqual(c.key_funding("bybit", "ethusdt"), "funding:bybit:ETHUSDT")
        self.assertEqual(c.key_oi("okx", "solusdt"), "oi:okx:SOLUSDT")
        self.assertEqual(c.key_orderbook("binance", "dogeusdt"), "orderbook:binance:DOGEUSDT")
        self.assertEqual(c.key_feature("btcusdt", "1h", "v1"), "feature:BTCUSDT:1h:v1")
        self.assertEqual(c.key_prediction("btcusdt", "1h"), "prediction:BTCUSDT:1h")
        self.assertEqual(c.key_provider_health("binance"), "provider:health:binance")

    def test_financial_cache_envelope_contract(self):
        sample_data = {"price": 95000.0, "symbol": "BTCUSDT"}
        envelope = RedisKeyContract.format_financial_envelope(
            data=sample_data,
            source="binance",
            ttl_seconds=5
        )
        self.assertEqual(envelope["payload"]["price"], 95000.0)
        self.assertEqual(envelope["source"], "binance")
        self.assertIn("updated_at", envelope)
        self.assertIn("freshness", envelope)
        self.assertEqual(envelope["ttl"], 5)
        # Verify JSON serializability
        serialized = json.dumps(envelope)
        self.assertIn("BTCUSDT", serialized)


if __name__ == "__main__":
    unittest.main()
