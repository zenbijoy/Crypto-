"""
CryptoScope AI - Canonical Strongly-Typed Domain Models (Step 6)
Implements Section 6 Canonical Data Models:
- Instrument, Ticker, Candle, Trade, AggTrade, OrderBookSnapshot, OrderBookDelta,
  FundingRate, OpenInterest, LongShortRatio, TakerFlow, LiquidationEvent,
  MarkPrice, IndexPrice, ProviderHealth.
- Every object strictly contains: provider, symbol, market_type, event_time, available_time, ingested_at.
- Strict UTC datetime handling.
"""
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator
from core.enums import Provider, MarketType, ContractType


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class CanonicalBaseModel(BaseModel):
    provider: Provider = Field(..., description="Exchange provider (BINANCE, BYBIT, OKX, etc.)")
    symbol: str = Field(..., description="Canonical trading symbol (e.g. BTCUSDT)")
    market_type: MarketType = Field(default=MarketType.PERPETUAL, description="SPOT, PERPETUAL, or DELIVERY")
    event_time: datetime = Field(..., description="Exchange server occurrence timestamp in UTC")
    available_time: datetime = Field(default_factory=utc_now, description="Point-in-time timestamp when data became visible to client in UTC")
    ingested_at: datetime = Field(default_factory=utc_now, description="Internal system ingestion timestamp in UTC")

    model_config = {
        "use_enum_values": True,
        "arbitrary_types_allowed": True
    }

    @field_validator("event_time", "available_time", "ingested_at", mode="before")
    def ensure_utc(cls, v):
        if isinstance(v, (int, float)):
            # Milliseconds epoch handling
            if v > 1e11:
                return datetime.fromtimestamp(v / 1000.0, tz=timezone.utc)
            return datetime.fromtimestamp(v, tz=timezone.utc)
        if isinstance(v, datetime):
            if v.tzinfo is None:
                return v.replace(tzinfo=timezone.utc)
            return v.astimezone(timezone.utc)
        return v


class Instrument(CanonicalBaseModel):
    instrument_id: str
    base_asset: str
    quote_asset: str
    contract_type: ContractType = ContractType.LINEAR
    tick_size: float
    step_size: float
    min_quantity: float
    min_notional: float = 5.0
    contract_size: float = 1.0
    settlement_asset: str = "USDT"
    is_active: bool = True
    is_memecoin: bool = False
    is_stablecoin: bool = False


class Ticker(CanonicalBaseModel):
    price: float
    bid_price: float
    ask_price: float
    bid_qty: float = 0.0
    ask_qty: float = 0.0
    volume_24h_base: float
    volume_24h_quote: float
    change_24h_pct: float
    high_24h: float
    low_24h: float


class Candle(CanonicalBaseModel):
    timeframe: str  # 1m, 5m, 15m, 30m, 1h, 4h, 1d
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
    taker_buy_quote: float = 0.0
    is_closed: bool = True


class Trade(CanonicalBaseModel):
    trade_id: str
    price: float
    quantity_base: float
    quantity_quote: float
    side: str  # BUY or SELL
    is_buyer_maker: bool


class AggTrade(CanonicalBaseModel):
    agg_trade_id: int
    price: float
    quantity_base: float
    first_trade_id: int
    last_trade_id: int
    is_buyer_maker: bool


class OrderBookSnapshot(CanonicalBaseModel):
    last_update_id: int
    bids: List[List[float]] = Field(..., description="[[price, qty], ...]")
    asks: List[List[float]] = Field(..., description="[[price, qty], ...]")
    spread_bps: float
    mid_price: float
    microprice: float
    imbalance_10bps: float
    depth_5bps_usd: float = 0.0
    depth_10bps_usd: float = 0.0


class OrderBookDelta(CanonicalBaseModel):
    first_update_id: int
    final_update_id: int
    previous_final_update_id: Optional[int] = None
    bids: List[List[float]] = Field(..., description="[[price, qty_delta], ...]")
    asks: List[List[float]] = Field(..., description="[[price, qty_delta], ...]")


class FundingRate(CanonicalBaseModel):
    rate: float
    funding_time: datetime
    mark_price: Optional[float] = None
    annualized_rate_pct: float
    predicted_rate: Optional[float] = None


class OpenInterest(CanonicalBaseModel):
    open_interest_usd: float
    open_interest_contracts: float


class LongShortRatio(CanonicalBaseModel):
    ratio_type: str  # GLOBAL_ACCOUNT, TOP_ACCOUNT, TOP_POSITION
    long_account_ratio: float
    short_account_ratio: float
    long_short_ratio: float


class TakerFlow(CanonicalBaseModel):
    buy_volume_usd: float
    sell_volume_usd: float
    buy_sell_ratio: float
    net_taker_volume_usd: float


class LiquidationEvent(CanonicalBaseModel):
    order_id: str
    side: str  # BUY (short liquidation) or SELL (long liquidation)
    price: float
    quantity: float
    notional_usd: float


class MarkPrice(CanonicalBaseModel):
    mark_price: float
    index_price: float
    estimated_settle_price: Optional[float] = None
    last_funding_rate: float
    next_funding_time: datetime


class IndexPrice(CanonicalBaseModel):
    index_price: float


class BookTicker(CanonicalBaseModel):
    best_bid_price: float
    best_bid_qty: float
    best_ask_price: float
    best_ask_qty: float


class PremiumIndex(CanonicalBaseModel):
    mark_price: float
    index_price: float
    estimated_settle_price: Optional[float] = None
    last_funding_rate: float
    next_funding_time: datetime
    interest_rate: float = 0.0001


class FeatureValue(BaseModel):
    feature_name: str
    value: Any
    event_time: datetime
    available_time: datetime
    source: str
    version: str = "2.1.0"
    quality: str = "REAL_EXCHANGE_DATA"
    provenance: Optional[Dict[str, Any]] = None

    model_config = {
        "arbitrary_types_allowed": True
    }


class ProviderHealth(BaseModel):
    provider: Provider
    status: str  # HEALTHY, DEGRADED, DOWN
    latency_ms: float
    used_weight_1m: int
    last_event_time: datetime
    error_count_1h: int = 0
    circuit_breaker_state: str = "CLOSED"
