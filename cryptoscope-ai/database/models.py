"""
CryptoScope AI - SQLAlchemy ORM Domain Models
Covers all minimum database tables defined in Specification Section 42.
"""
from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, JSON, Text, ForeignKey, Index
)
from database.session import Base

def utcnow():
    return datetime.now(timezone.utc)

class AssetModel(Base):
    __tablename__ = "assets"
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), unique=True, nullable=False, index=True)  # BTC, ETH, SOL
    name = Column(String(50), nullable=False)
    decimals = Column(Integer, default=8)
    created_at = Column(DateTime, default=utcnow)

class ExchangeModel(Base):
    __tablename__ = "exchanges"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False) # BINANCE, BYBIT, OKX
    name = Column(String(50), nullable=False)
    status = Column(String(20), default="ACTIVE")

class CandleModel(Base):
    __tablename__ = "candles"
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    resolution = Column(String(10), nullable=False, index=True) # 1m, 5m, 15m, 1h, 4h, 1d
    timestamp = Column(DateTime, nullable=False, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    quote_volume = Column(Float, default=0.0)
    taker_buy_volume = Column(Float, default=0.0)
    trades_count = Column(Integer, default=0)

    __table_args__ = (
        Index("idx_candles_sym_res_ts", "symbol", "resolution", "timestamp", unique=True),
    )

class OrderbookSnapshotModel(Base):
    __tablename__ = "orderbook_snapshots"
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    exchange = Column(String(20), default="BINANCE")
    timestamp = Column(DateTime, nullable=False, index=True)
    bid_depth_5bps = Column(Float, default=0.0)
    ask_depth_5bps = Column(Float, default=0.0)
    bid_depth_10bps = Column(Float, default=0.0)
    ask_depth_10bps = Column(Float, default=0.0)
    bid_depth_25bps = Column(Float, default=0.0)
    ask_depth_25bps = Column(Float, default=0.0)
    bid_depth_50bps = Column(Float, default=0.0)
    ask_depth_50bps = Column(Float, default=0.0)
    spread_bps = Column(Float, default=0.0)
    microprice = Column(Float, default=0.0)
    imbalance_10bps = Column(Float, default=0.0)
    book_convexity = Column(Float, default=0.0)

class FundingRateModel(Base):
    __tablename__ = "funding_rates"
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    exchange = Column(String(20), default="BINANCE")
    timestamp = Column(DateTime, nullable=False, index=True)
    rate = Column(Float, nullable=False)
    rate_7d_zscore = Column(Float, default=0.0)
    predicted_rate = Column(Float, default=0.0)
    annualized_rate = Column(Float, default=0.0)

class OpenInterestModel(Base):
    __tablename__ = "open_interest"
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    exchange = Column(String(20), default="BINANCE")
    timestamp = Column(DateTime, nullable=False, index=True)
    open_interest_usd = Column(Float, nullable=False)
    oi_change_1h = Column(Float, default=0.0)
    oi_velocity = Column(Float, default=0.0)

class LiquidationModel(Base):
    __tablename__ = "liquidations"
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    long_liq_usd = Column(Float, default=0.0)
    short_liq_usd = Column(Float, default=0.0)
    liquidation_pressure_score = Column(Float, default=0.0)
    cascade_state = Column(String(20), default="NORMAL")

class OnChainMetricModel(Base):
    __tablename__ = "onchain_metrics"
    id = Column(Integer, primary_key=True, index=True)
    asset = Column(String(10), nullable=False, index=True) # BTC, ETH, SOL
    timestamp = Column(DateTime, nullable=False, index=True)
    exchange_netflow_usd = Column(Float, default=0.0)
    whale_deposit_count = Column(Integer, default=0)
    sopr = Column(Float, default=1.0)
    mvrv = Column(Float, default=1.5)
    active_addresses = Column(Integer, default=0)

class MacroMetricModel(Base):
    __tablename__ = "macro_metrics"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    dxy_index = Column(Float, default=104.2)
    us_10y_yield = Column(Float, default=4.25)
    us_2y_yield = Column(Float, default=4.65)
    vix_index = Column(Float, default=14.8)
    sp500_return_1d = Column(Float, default=0.0)

class PredictionRecordModel(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    horizon = Column(String(10), nullable=False, index=True) # 1m, 5m, 15m, 1h, 4h, 1d
    timestamp = Column(DateTime, nullable=False, index=True)
    current_price = Column(Float, nullable=False)
    expected_return = Column(Float, default=0.0)
    direction = Column(String(10), nullable=False) # UP, DOWN, SIDEWAYS
    p_up = Column(Float, nullable=False)
    p_down = Column(Float, nullable=False)
    p_sideways = Column(Float, nullable=False)
    price_p10 = Column(Float, nullable=False)
    price_p25 = Column(Float, nullable=False)
    price_p50 = Column(Float, nullable=False)
    price_p75 = Column(Float, nullable=False)
    price_p90 = Column(Float, nullable=False)
    expected_volatility = Column(Float, default=0.0)
    confidence = Column(Integer, default=0) # 0-100
    model_agreement = Column(Integer, default=0) # 0-100
    regime = Column(String(50), default="SIDEWAYS")
    data_quality = Column(Integer, default=100)
    signal = Column(String(20), default="NEUTRAL / NO-TRADE")
    signal_reason = Column(Text, default="")
    risk_level = Column(String(20), default="MEDIUM")
    model_version = Column(String(50), default="champion-v2.1")
    disclaimer = Column(String(200), default="Probabilistic market analysis — not a guarantee of future performance.")

class ModelVersionModel(Base):
    __tablename__ = "model_versions"
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), nullable=False, index=True)
    stage = Column(String(20), default="PRODUCTION") # EXPERIMENTAL, CANDIDATE, SHADOW, PRODUCTION
    brier_score = Column(Float, default=0.18)
    precision_score = Column(Float, default=0.74)
    coverage_pct = Column(Float, default=0.28)
    ece_score = Column(Float, default=0.04)
    last_retrained_at = Column(DateTime, default=utcnow)

class PaperTradeModel(Base):
    __tablename__ = "paper_trades"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), default="default_user", index=True)
    symbol = Column(String(20), nullable=False)
    direction = Column(String(10), nullable=False) # LONG, SHORT
    size_usd = Column(Float, nullable=False)
    entry_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)
    stop_loss = Column(Float, default=0.0)
    take_profit = Column(Float, default=0.0)
    leverage = Column(Integer, default=3)
    unrealized_pnl = Column(Float, default=0.0)
    status = Column(String(20), default="OPEN") # OPEN, CLOSED
    opened_at = Column(DateTime, default=utcnow)
    closed_at = Column(DateTime, nullable=True)

class AlertRuleModel(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False)
    horizon = Column(String(10), default="1h")
    min_confidence = Column(Integer, default=80)
    min_model_agreement = Column(Integer, default=75)
    signal_type = Column(String(20), default="LONG")
    is_active = Column(Boolean, default=True)
    cooldown_minutes = Column(Integer, default=60)
    last_triggered_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utcnow)

class TelegramUserModel(Base):
    __tablename__ = "telegram_users"
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(String(50), unique=True, nullable=False)
    username = Column(String(50), nullable=True)
    is_subscribed_alerts = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)

class AuditLogModel(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(100), nullable=False)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=utcnow)
