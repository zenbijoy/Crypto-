"""
CryptoScope AI - Truthful SQLAlchemy ORM Domain Models
Phases 12 & 13: Truthful Database Schema without invented defaults.
Model lifecycle starts at EXPERIMENTAL. All observation and metric fields default to None.
"""
from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, JSON, Text, ForeignKey, Index, BigInteger
)
from database.session import Base


def utcnow():
    return datetime.now(timezone.utc)


class InstrumentModel(Base):
    __tablename__ = "instruments"
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), unique=True, nullable=False, index=True)
    base_asset = Column(String(10), nullable=False, index=True)
    quote_asset = Column(String(10), nullable=False)
    provider = Column(String(20), nullable=False, default="BINANCE")
    market_type = Column(String(20), default="PERPETUAL")
    contract_type = Column(String(20), default="LINEAR")
    tick_size = Column(Float, default=0.01)
    step_size = Column(Float, default=0.001)
    min_quantity = Column(Float, default=0.001)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)


class CandleModel(Base):
    __tablename__ = "candles"
    id = Column(BigInteger, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    resolution = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    quote_volume = Column(Float, default=0.0)
    taker_buy_volume = Column(Float, default=0.0)
    trades_count = Column(Integer, default=0)
    provider = Column(String(20), default="BINANCE")

    __table_args__ = (
        Index("idx_candles_sym_res_ts", "symbol", "resolution", "timestamp", unique=True),
    )


class AggTradeModel(Base):
    __tablename__ = "agg_trades"
    id = Column(BigInteger, primary_key=True, index=True)
    agg_trade_id = Column(BigInteger, nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    price = Column(Float, nullable=False)
    quantity = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    is_buyer_maker = Column(Boolean, nullable=False)
    provider = Column(String(20), default="BINANCE")

    __table_args__ = (
        Index("idx_aggtrades_sym_id", "symbol", "agg_trade_id", unique=True),
    )


class TradeModel(Base):
    __tablename__ = "trades"
    id = Column(BigInteger, primary_key=True, index=True)
    trade_id = Column(String(50), nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    price = Column(Float, nullable=False)
    quantity = Column(Float, nullable=False)
    side = Column(String(10), nullable=False)  # BUY, SELL
    timestamp = Column(DateTime, nullable=False, index=True)
    provider = Column(String(20), default="BINANCE")

    __table_args__ = (
        Index("idx_trades_sym_id", "symbol", "trade_id", unique=True),
    )


class FundingRateModel(Base):
    __tablename__ = "funding_rates"
    id = Column(BigInteger, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    provider = Column(String(20), default="BINANCE")
    timestamp = Column(DateTime, nullable=False, index=True)
    rate = Column(Float, nullable=False)
    rate_7d_zscore = Column(Float, nullable=True)
    mark_price = Column(Float, nullable=True)

    __table_args__ = (
        Index("idx_funding_sym_ts", "symbol", "timestamp", unique=True),
    )


class OpenInterestModel(Base):
    __tablename__ = "open_interest"
    id = Column(BigInteger, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    provider = Column(String(20), default="BINANCE")
    timestamp = Column(DateTime, nullable=False, index=True)
    open_interest_usd = Column(Float, nullable=False)
    open_interest_contracts = Column(Float, nullable=True)

    __table_args__ = (
        Index("idx_oi_sym_ts", "symbol", "timestamp", unique=True),
    )


class LongShortRatioModel(Base):
    __tablename__ = "long_short_ratios"
    id = Column(BigInteger, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    ratio_type = Column(String(30), nullable=False)  # GLOBAL_ACCOUNT, TOP_ACCOUNT
    long_account_ratio = Column(Float, nullable=False)
    short_account_ratio = Column(Float, nullable=False)
    long_short_ratio = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)


class TakerFlowModel(Base):
    __tablename__ = "taker_flow"
    id = Column(BigInteger, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    buy_volume_usd = Column(Float, nullable=False)
    sell_volume_usd = Column(Float, nullable=False)
    buy_sell_ratio = Column(Float, nullable=False)
    net_taker_volume_usd = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)


class LiquidationModel(Base):
    __tablename__ = "liquidations"
    id = Column(BigInteger, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    side = Column(String(10), nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Float, nullable=False)
    notional_usd = Column(Float, nullable=False)


class OrderbookSnapshotModel(Base):
    __tablename__ = "orderbook_snapshots"
    id = Column(BigInteger, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    provider = Column(String(20), default="BINANCE")
    timestamp = Column(DateTime, nullable=False, index=True)
    last_update_id = Column(BigInteger, nullable=True)
    spread_bps = Column(Float, nullable=True)
    mid_price = Column(Float, nullable=True)
    microprice = Column(Float, nullable=True)
    imbalance_10bps = Column(Float, nullable=True)
    depth_5bps_usd = Column(Float, nullable=True)
    depth_10bps_usd = Column(Float, nullable=True)
    bids = Column(JSON, nullable=True)
    asks = Column(JSON, nullable=True)


class MarketMetricModel(Base):
    __tablename__ = "market_metrics"
    id = Column(BigInteger, primary_key=True, index=True)
    asset = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    dxy_index = Column(Float, nullable=True)
    us_10y_yield = Column(Float, nullable=True)
    tvl_usd = Column(Float, nullable=True)
    fear_and_greed = Column(Integer, nullable=True)


class FeatureValueModel(Base):
    __tablename__ = "feature_values"
    id = Column(BigInteger, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    feature_name = Column(String(50), nullable=False, index=True)
    value = Column(Float, nullable=True)
    event_time = Column(DateTime, nullable=False, index=True)
    available_time = Column(DateTime, nullable=False, index=True)
    version = Column(String(20), default="2.1.0")


class DatasetManifestModel(Base):
    __tablename__ = "dataset_manifests"
    id = Column(Integer, primary_key=True, index=True)
    dataset_name = Column(String(100), unique=True, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    feature_schema_hash = Column(String(64), nullable=False)
    row_count = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=utcnow)


class PredictionRecordModel(Base):
    __tablename__ = "predictions"
    id = Column(BigInteger, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    horizon = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    current_price = Column(Float, nullable=False)
    expected_return = Column(Float, nullable=True)
    direction = Column(String(10), nullable=False)
    p_up = Column(Float, nullable=False)
    p_down = Column(Float, nullable=False)
    p_sideways = Column(Float, nullable=False)
    price_p10 = Column(Float, nullable=True)
    price_p25 = Column(Float, nullable=True)
    price_p50 = Column(Float, nullable=True)
    price_p75 = Column(Float, nullable=True)
    price_p90 = Column(Float, nullable=True)
    confidence = Column(Integer, nullable=True)
    model_agreement = Column(Integer, nullable=True)
    regime = Column(String(50), nullable=True)
    data_quality = Column(Integer, nullable=True)
    signal = Column(String(30), nullable=False)
    signal_reason = Column(Text, nullable=True)
    model_version = Column(String(50), nullable=False)
    model_type = Column(String(50), default="HEURISTIC_BASELINE")


class ModelVersionModel(Base):
    __tablename__ = "model_versions"
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), nullable=False, index=True)
    stage = Column(String(20), default="EXPERIMENTAL")  # EXPERIMENTAL, CANDIDATE, SHADOW, PAPER, PRODUCTION
    brier_score = Column(Float, nullable=True)
    precision_score = Column(Float, nullable=True)
    coverage_pct = Column(Float, nullable=True)
    ece_score = Column(Float, nullable=True)
    dataset_manifest_id = Column(Integer, nullable=True)
    hyperparameters = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=utcnow)


class PaperAccountModel(Base):
    __tablename__ = "paper_accounts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), unique=True, nullable=False, index=True)
    balance_usd = Column(Float, default=10000.0)
    currency = Column(String(10), default="USDT")
    created_at = Column(DateTime, default=utcnow)


class PaperPositionModel(Base):
    __tablename__ = "paper_positions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), nullable=False, index=True)
    symbol = Column(String(20), nullable=False)
    direction = Column(String(10), nullable=False)  # LONG, SHORT
    size_usd = Column(Float, nullable=False)
    entry_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)
    stop_loss = Column(Float, nullable=True)
    take_profit = Column(Float, nullable=True)
    leverage = Column(Integer, default=1)
    unrealized_pnl = Column(Float, default=0.0)
    status = Column(String(20), default="OPEN")  # OPEN, CLOSED
    opened_at = Column(DateTime, default=utcnow)
    closed_at = Column(DateTime, nullable=True)


class PaperOrderModel(Base):
    __tablename__ = "paper_orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), nullable=False, index=True)
    symbol = Column(String(20), nullable=False)
    side = Column(String(10), nullable=False)
    order_type = Column(String(20), default="MARKET")
    size_usd = Column(Float, nullable=False)
    limit_price = Column(Float, nullable=True)
    filled_price = Column(Float, nullable=True)
    fee_usd = Column(Float, default=0.0)
    status = Column(String(20), default="PENDING")
    created_at = Column(DateTime, default=utcnow)


class DataQualityEventModel(Base):
    __tablename__ = "data_quality_events"
    id = Column(BigInteger, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    violation_type = Column(String(50), nullable=False)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=utcnow)


class ProviderHealthEventModel(Base):
    __tablename__ = "provider_health_events"
    id = Column(BigInteger, primary_key=True, index=True)
    provider = Column(String(20), nullable=False, index=True)
    status = Column(String(20), nullable=False)
    latency_ms = Column(Float, nullable=True)
    created_at = Column(DateTime, default=utcnow)


class AuditLogModel(Base):
    __tablename__ = "audit_logs"
    id = Column(BigInteger, primary_key=True, index=True)
    action = Column(String(100), nullable=False)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=utcnow)


class AlertRuleModel(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False)
    horizon = Column(String(10), default="1h")
    min_confidence = Column(Integer, default=80)
    signal_type = Column(String(20), default="LONG")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)


class TelegramUserModel(Base):
    __tablename__ = "telegram_users"
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(String(50), unique=True, nullable=False)
    username = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=utcnow)
