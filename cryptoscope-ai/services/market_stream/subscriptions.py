"""
CryptoScope AI - Market Stream Subscription Registry
Manages upstream exchange WebSocket stream subscriptions for Tier-1 and broader assets.
"""
from typing import Set, List
from enum import Enum


class StreamType(str, Enum):
    AGG_TRADE = "aggTrade"
    BOOK_TICKER = "bookTicker"
    DEPTH = "depth@100ms"
    KLINE_1M = "kline_1m"
    MARK_PRICE = "markPrice@1s"
    LIQUIDATION = "forceOrder"


class StreamSubscriptionManager:
    """Tracks active and requested subscriptions for exchange stream connections."""
    def __init__(self):
        self._subscriptions: Set[str] = set()

    def add_subscription(self, symbol: str, stream_type: StreamType):
        stream_name = f"{symbol.lower()}@{stream_type.value}"
        self._subscriptions.add(stream_name)

    def remove_subscription(self, symbol: str, stream_type: StreamType):
        stream_name = f"{symbol.lower()}@{stream_type.value}"
        self._subscriptions.discard(stream_name)

    def get_all_streams(self) -> List[str]:
        return sorted(list(self._subscriptions))

    def setup_default_tier1_streams(self, symbols: List[str] = None):
        target_symbols = symbols or ["BTCUSDT", "ETHUSDT", "SOLUSDT", "DOGEUSDT"]
        for sym in target_symbols:
            self.add_subscription(sym, StreamType.AGG_TRADE)
            self.add_subscription(sym, StreamType.BOOK_TICKER)
            self.add_subscription(sym, StreamType.DEPTH)
            self.add_subscription(sym, StreamType.MARK_PRICE)

stream_registry = StreamSubscriptionManager()
