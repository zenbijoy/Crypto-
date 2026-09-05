-- =========================================================
-- CryptoScope AI — TimescaleDB & PostgreSQL Initialization
-- Implements Step 7: Time-series hypertables, indexes,
-- compression policies, retention policies, and unique constraints.
-- =========================================================

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- Canonical Schemas (Phase 8)
CREATE SCHEMA IF NOT EXISTS product;
CREATE SCHEMA IF NOT EXISTS quant;
CREATE SCHEMA IF NOT EXISTS mlops;
CREATE SCHEMA IF NOT EXISTS audit;

-- 1. Candlesticks (OHLCV)
CREATE TABLE IF NOT EXISTS candles (
    timestamp TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    resolution VARCHAR(10) NOT NULL,
    provider VARCHAR(20) DEFAULT 'BINANCE',
    open DOUBLE PRECISION NOT NULL,
    high DOUBLE PRECISION NOT NULL,
    low DOUBLE PRECISION NOT NULL,
    close DOUBLE PRECISION NOT NULL,
    volume DOUBLE PRECISION NOT NULL,
    quote_volume DOUBLE PRECISION DEFAULT 0.0,
    trades_count INT DEFAULT 0,
    taker_buy_volume DOUBLE PRECISION DEFAULT 0.0,
    is_closed BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT pk_candles PRIMARY KEY (symbol, resolution, timestamp)
);
SELECT create_hypertable('candles', 'timestamp', if_not_exists => TRUE, chunk_time_interval => INTERVAL '7 days');
CREATE INDEX IF NOT EXISTS idx_candles_sym_ts ON candles (symbol, timestamp DESC);

-- 2. Trades & AggTrades
CREATE TABLE IF NOT EXISTS trades (
    timestamp TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    trade_id VARCHAR(50) NOT NULL,
    provider VARCHAR(20) DEFAULT 'BINANCE',
    price DOUBLE PRECISION NOT NULL,
    quantity DOUBLE PRECISION NOT NULL,
    quote_quantity DOUBLE PRECISION NOT NULL,
    side VARCHAR(10) NOT NULL,
    is_buyer_maker BOOLEAN DEFAULT FALSE,
    CONSTRAINT pk_trades PRIMARY KEY (symbol, trade_id, timestamp)
);
SELECT create_hypertable('trades', 'timestamp', if_not_exists => TRUE, chunk_time_interval => INTERVAL '1 day');
CREATE INDEX IF NOT EXISTS idx_trades_sym_ts ON trades (symbol, timestamp DESC);

-- 3. Order Book Depth Snapshots
CREATE TABLE IF NOT EXISTS orderbook_snapshots (
    timestamp TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    provider VARCHAR(20) DEFAULT 'BINANCE',
    last_update_id BIGINT NOT NULL,
    spread_bps DOUBLE PRECISION DEFAULT 0.0,
    mid_price DOUBLE PRECISION NOT NULL,
    microprice DOUBLE PRECISION NOT NULL,
    imbalance_10bps DOUBLE PRECISION DEFAULT 0.0,
    depth_5bps_usd DOUBLE PRECISION DEFAULT 0.0,
    depth_10bps_usd DOUBLE PRECISION DEFAULT 0.0,
    bids JSONB NOT NULL,
    asks JSONB NOT NULL,
    CONSTRAINT pk_orderbook PRIMARY KEY (symbol, timestamp)
);
SELECT create_hypertable('orderbook_snapshots', 'timestamp', if_not_exists => TRUE, chunk_time_interval => INTERVAL '1 day');
CREATE INDEX IF NOT EXISTS idx_orderbook_sym_ts ON orderbook_snapshots (symbol, timestamp DESC);

-- 4. Funding Rates
CREATE TABLE IF NOT EXISTS funding_rates (
    timestamp TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    provider VARCHAR(20) DEFAULT 'BINANCE',
    rate DOUBLE PRECISION NOT NULL,
    predicted_rate DOUBLE PRECISION DEFAULT 0.0,
    rate_7d_zscore DOUBLE PRECISION DEFAULT 0.0,
    annualized_rate DOUBLE PRECISION DEFAULT 0.0,
    mark_price DOUBLE PRECISION DEFAULT 0.0,
    CONSTRAINT pk_funding_rates PRIMARY KEY (symbol, timestamp)
);
SELECT create_hypertable('funding_rates', 'timestamp', if_not_exists => TRUE, chunk_time_interval => INTERVAL '30 days');
CREATE INDEX IF NOT EXISTS idx_funding_sym_ts ON funding_rates (symbol, timestamp DESC);

-- 5. Open Interest
CREATE TABLE IF NOT EXISTS open_interest (
    timestamp TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    provider VARCHAR(20) DEFAULT 'BINANCE',
    open_interest_usd DOUBLE PRECISION NOT NULL,
    open_interest_contracts DOUBLE PRECISION DEFAULT 0.0,
    oi_velocity DOUBLE PRECISION DEFAULT 0.0,
    CONSTRAINT pk_open_interest PRIMARY KEY (symbol, timestamp)
);
SELECT create_hypertable('open_interest', 'timestamp', if_not_exists => TRUE, chunk_time_interval => INTERVAL '14 days');
CREATE INDEX IF NOT EXISTS idx_oi_sym_ts ON open_interest (symbol, timestamp DESC);

-- 6. Long/Short Ratios & Taker Flow
CREATE TABLE IF NOT EXISTS derivatives_ratios (
    timestamp TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    provider VARCHAR(20) DEFAULT 'BINANCE',
    ratio_type VARCHAR(30) NOT NULL, -- GLOBAL_ACCOUNT, TOP_ACCOUNT, TOP_POSITION, TAKER_RATIO
    long_ratio DOUBLE PRECISION DEFAULT 0.0,
    short_ratio DOUBLE PRECISION DEFAULT 0.0,
    long_short_ratio DOUBLE PRECISION NOT NULL,
    CONSTRAINT pk_derivatives_ratios PRIMARY KEY (symbol, ratio_type, timestamp)
);
SELECT create_hypertable('derivatives_ratios', 'timestamp', if_not_exists => TRUE, chunk_time_interval => INTERVAL '14 days');

-- 7. Liquidations
CREATE TABLE IF NOT EXISTS liquidations (
    timestamp TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    provider VARCHAR(20) DEFAULT 'BINANCE',
    side VARCHAR(10) NOT NULL,
    price DOUBLE PRECISION NOT NULL,
    quantity DOUBLE PRECISION NOT NULL,
    notional_usd DOUBLE PRECISION NOT NULL,
    cascade_state VARCHAR(20) DEFAULT 'NORMAL',
    CONSTRAINT pk_liquidations PRIMARY KEY (symbol, timestamp, price, side)
);
SELECT create_hypertable('liquidations', 'timestamp', if_not_exists => TRUE, chunk_time_interval => INTERVAL '14 days');

-- 8. Feature Values (Point-In-Time Leak-Free Store)
CREATE TABLE IF NOT EXISTS feature_values (
    timestamp TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    feature_name VARCHAR(60) NOT NULL,
    feature_value DOUBLE PRECISION NOT NULL,
    available_time TIMESTAMPTZ NOT NULL,
    source VARCHAR(30) DEFAULT 'BINANCE',
    version VARCHAR(20) DEFAULT 'v1',
    quality_score INT DEFAULT 100,
    CONSTRAINT pk_feature_values PRIMARY KEY (symbol, feature_name, timestamp)
);
SELECT create_hypertable('feature_values', 'timestamp', if_not_exists => TRUE, chunk_time_interval => INTERVAL '7 days');
CREATE INDEX IF NOT EXISTS idx_feat_sym_avail ON feature_values (symbol, available_time DESC);

-- 9. Predictions
CREATE TABLE IF NOT EXISTS predictions (
    timestamp TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    horizon VARCHAR(10) NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    model_type VARCHAR(50) DEFAULT 'EXPERIMENTAL_HEURISTIC',
    current_price DOUBLE PRECISION NOT NULL,
    direction VARCHAR(10) NOT NULL,
    expected_return_pct DOUBLE PRECISION NOT NULL,
    p10 DOUBLE PRECISION NOT NULL,
    p25 DOUBLE PRECISION NOT NULL,
    p50 DOUBLE PRECISION NOT NULL,
    p75 DOUBLE PRECISION NOT NULL,
    p90 DOUBLE PRECISION NOT NULL,
    calibrated_confidence INT DEFAULT 0,
    is_abstaining BOOLEAN DEFAULT FALSE,
    abstention_reason TEXT DEFAULT '',
    CONSTRAINT pk_predictions PRIMARY KEY (symbol, horizon, timestamp)
);
SELECT create_hypertable('predictions', 'timestamp', if_not_exists => TRUE, chunk_time_interval => INTERVAL '7 days');

-- 10. Data Quality Events
CREATE TABLE IF NOT EXISTS data_quality_events (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    symbol VARCHAR(20) NOT NULL,
    event_type VARCHAR(50) NOT NULL, -- GAP_DETECTED, OHLC_VIOLATION, NEGATIVE_SPREAD, SEQUENCE_GAP
    severity VARCHAR(20) NOT NULL,   -- WARNING, CRITICAL, REJECTED
    description TEXT NOT NULL,
    details JSONB
);
CREATE INDEX IF NOT EXISTS idx_dq_sym_ts ON data_quality_events (symbol, timestamp DESC);

-- TimescaleDB Compression Policies
ALTER TABLE candles SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'symbol, resolution'
);
SELECT add_compression_policy('candles', INTERVAL '14 days', if_not_exists => TRUE);

-- Retention Policies
SELECT add_retention_policy('candles', INTERVAL '365 days', if_not_exists => TRUE);
SELECT add_retention_policy('trades', INTERVAL '30 days', if_not_exists => TRUE);
SELECT add_retention_policy('orderbook_snapshots', INTERVAL '14 days', if_not_exists => TRUE);
