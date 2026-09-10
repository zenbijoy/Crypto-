"""
CryptoScope AI - Base Exchange Provider Interface
Normalized interfaces for Binance, Bybit, and OKX derivatives data.
Every observation strictly captures provenance:
provider, symbol, canonical_symbol, market_type, event_time, available_time, ingested_at, source_endpoint, quality.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

try:
    from pydantic import BaseModel, Field
except ImportError:
    from dataclasses import dataclass, field

    class BaseModel:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    def Field(default=None, default_factory=None, **kwargs):
        if default_factory is not None:
            return field(default_factory=default_factory)
        return field(default=default)


class NormalizedObservation(BaseModel):
    provider: str
    symbol: str
    canonical_symbol: str
    market_type: str = "PERP"
    event_time: datetime
    available_time: datetime
    ingested_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source_endpoint: str
    quality: float = 100.0  # 0 to 100 data quality score


class TickerData(NormalizedObservation):
    last_price: float
    mark_price: Optional[float] = None
    index_price: Optional[float] = None
    high_24h: Optional[float] = None
    low_24h: Optional[float] = None
    volume_24h: Optional[float] = None
    quote_volume_24h: Optional[float] = None
    open_interest: Optional[float] = None
    funding_rate: Optional[float] = None
    next_funding_time: Optional[datetime] = None
    price_change_pct_24h: Optional[float] = 0.0


class BookTickerData(NormalizedObservation):
    bid_price: float
    bid_size: float
    ask_price: float
    ask_size: float


class CandleData(NormalizedObservation):
    interval: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    quote_volume: float
    trades_count: Optional[int] = None
    taker_buy_base: Optional[float] = None
    taker_buy_quote: Optional[float] = None


class TradeData(NormalizedObservation):
    trade_id: str
    price: float
    size: float
    side: str  # "buy" or "sell"
    is_buyer_maker: bool


class OrderBookData(NormalizedObservation):
    bids: List[List[float]]  # [[price, size], ...]
    asks: List[List[float]]  # [[price, size], ...]
    sequence: Optional[int] = None


class FundingData(NormalizedObservation):
    funding_rate: float
    funding_time: datetime
    predicted_rate: Optional[float] = None


class OpenInterestData(NormalizedObservation):
    open_interest: float
    unit: str  # "COIN", "CONTRACT", or "USD"
    normalized_notional_usd: float
    conversion_price: float


class LiquidationData(NormalizedObservation):
    side: str  # "buy" (short liquidating) or "sell" (long liquidating)
    price: float
    size: float
    notional_usd: float


class BaseExchangeProvider(ABC):
    """Abstract interface for all supported crypto derivatives exchanges."""

    def __init__(self, provider_name: str, base_url: str):
        self.provider_name = provider_name
        self.base_url = base_url

    @abstractmethod
    async def get_ticker(self, canonical_symbol: str) -> TickerData:
        pass

    @abstractmethod
    async def get_book_ticker(self, canonical_symbol: str) -> BookTickerData:
        pass

    @abstractmethod
    async def get_candles(self, canonical_symbol: str, interval: str, limit: int = 100) -> List[CandleData]:
        pass

    @abstractmethod
    async def get_trades(self, canonical_symbol: str, limit: int = 100) -> List[TradeData]:
        pass

    @abstractmethod
    async def get_orderbook(self, canonical_symbol: str, depth: int = 50) -> OrderBookData:
        pass

    @abstractmethod
    async def get_funding(self, canonical_symbol: str) -> FundingData:
        pass

    @abstractmethod
    async def get_open_interest(self, canonical_symbol: str) -> OpenInterestData:
        pass

    @abstractmethod
    async def get_mark_price(self, canonical_symbol: str) -> float:
        pass

    @abstractmethod
    async def get_index_price(self, canonical_symbol: str) -> float:
        pass

    @abstractmethod
    async def get_liquidations(self, canonical_symbol: str, limit: int = 50) -> List[LiquidationData]:
        pass

    @abstractmethod
    async def health(self) -> Dict[str, Any]:
        pass
