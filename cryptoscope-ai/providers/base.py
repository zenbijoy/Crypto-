"""
CryptoScope AI - Base Provider Interfaces & Abstract Protocols
Implements Section 2: Canonical Provider Architecture.
All external providers must implement these standardized interfaces and return canonical DTOs.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncGenerator
from dataclasses import dataclass
from datetime import datetime
from core.enums import Provider, MarketType, ContractType

@dataclass
class CanonicalInstrument:
    instrument_id: str             # e.g. BINANCE:BTCUSDT:PERPETUAL
    canonical_symbol: str          # e.g. BTCUSDT
    base_asset: str                # e.g. BTC
    quote_asset: str               # e.g. USDT
    provider: Provider
    provider_symbol: str           # e.g. BTCUSDT, BTC-USDT-SWAP, BTC-USD
    market_type: MarketType
    contract_type: ContractType
    tick_size: float
    step_size: float
    min_quantity: float
    contract_size: float = 1.0
    settlement_asset: Optional[str] = "USDT"
    is_active: bool = True
    listing_time: Optional[datetime] = None
    is_stablecoin: bool = False
    is_memecoin: bool = False

@dataclass
class CanonicalTicker:
    provider: Provider
    instrument_id: str
    symbol: str
    base_asset: str
    quote_asset: str
    price: float
    bid_price: float
    ask_price: float
    volume_24h_base: float
    volume_24h_quote: float
    change_24h_pct: float
    high_24h: float
    low_24h: float
    timestamp: datetime

@dataclass
class CanonicalCandle:
    provider: Provider
    instrument_id: str
    timeframe: str                 # 1m, 5m, 15m, 1h, 4h, 1d
    open_time: datetime
    close_time: datetime
    open: float
    high: float
    low: float
    close: float
    volume_base: float
    volume_quote: float
    trade_count: int
    taker_buy_base: float = 0.0
    is_closed: bool = True

@dataclass
class CanonicalTrade:
    provider: Provider
    instrument_id: str
    trade_id: str
    timestamp: datetime
    price: float
    quantity_base: float
    quantity_quote: float
    side: str                      # BUY or SELL
    is_buyer_maker: bool

@dataclass
class CanonicalOrderBook:
    provider: Provider
    instrument_id: str
    timestamp: datetime
    bids: List[List[float]]        # [[price, size], ...]
    asks: List[List[float]]        # [[price, size], ...]
    spread_bps: float
    mid_price: float
    microprice: float
    imbalance_10bps: float

@dataclass
class CanonicalDerivativesSnapshot:
    provider: Provider
    instrument_id: str
    timestamp: datetime
    funding_rate: Optional[float] = None
    predicted_funding_rate: Optional[float] = None
    funding_rate_7d_zscore: Optional[float] = None
    open_interest_usd: Optional[float] = None
    open_interest_contracts: Optional[float] = None
    mark_price: Optional[float] = None
    index_price: Optional[float] = None
    basis_bps: Optional[float] = None
    long_short_ratio: Optional[float] = None
    top_trader_ratio: Optional[float] = None
    taker_buy_sell_ratio: Optional[float] = None
    long_liquidation_usd: Optional[float] = None
    short_liquidation_usd: Optional[float] = None

class MarketDataProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> Provider:
        pass

    @abstractmethod
    async def discover_instruments(self) -> List[CanonicalInstrument]:
        """Discovers all available spot and derivatives instruments from provider exchange metadata."""
        pass

    @abstractmethod
    async def fetch_ticker(self, instrument: CanonicalInstrument) -> CanonicalTicker:
        pass

    @abstractmethod
    async def fetch_tickers(self) -> List[CanonicalTicker]:
        pass

    @abstractmethod
    async def fetch_ohlcv(
        self, instrument: CanonicalInstrument, timeframe: str, start: Optional[datetime] = None, end: Optional[datetime] = None, limit: int = 100
    ) -> List[CanonicalCandle]:
        pass

    @abstractmethod
    async def fetch_trades(self, instrument: CanonicalInstrument, limit: int = 100) -> List[CanonicalTrade]:
        pass

    @abstractmethod
    async def fetch_orderbook(self, instrument: CanonicalInstrument, depth: int = 50) -> CanonicalOrderBook:
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        pass

class DerivativesProvider(ABC):
    @abstractmethod
    async def fetch_open_interest(self, instrument: CanonicalInstrument) -> float:
        pass

    @abstractmethod
    async def fetch_funding_rate(self, instrument: CanonicalInstrument) -> float:
        pass

    @abstractmethod
    async def fetch_derivatives_snapshot(self, instrument: CanonicalInstrument) -> CanonicalDerivativesSnapshot:
        pass

class OptionalDataProvider(ABC):
    @abstractmethod
    async def fetch_metrics(self, asset: str) -> Dict[str, Any]:
        pass
