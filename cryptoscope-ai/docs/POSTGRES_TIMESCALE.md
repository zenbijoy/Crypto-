# CryptoScope AI — PostgreSQL & TimescaleDB Architecture

**Database Schemas, Hypertables, Retention Policies & Alembic Migrations**  

---

## 1. Schema Separation Design

The unified relational and time-series database is partitioned into four distinct logical schemas:

1. **`product`**: Manages user profiles, preferences, watchlists, alert rules, FCM device tokens, and paper accounts.
2. **`quant`**: Manages high-throughput market data, candles, executions, orderbook metrics, funding rates, open interest, and prediction records.
3. **`mlops`**: Tracks model registry metadata, dataset manifests, backtest performance logs, and drift detector metrics.
4. **`audit`**: Stores administrative actions, model deployment promotions/rollbacks, and security events.

---

## 2. TimescaleDB Hypertables & Compression

High-frequency quantitative tables in the `quant` schema are converted into TimescaleDB hypertables partitioned by `timestamp`:

```sql
-- Enable TimescaleDB Extension
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- Convert Candles to Hypertable (1-day chunks)
SELECT create_hypertable('quant.candles', 'timestamp', chunk_time_interval => INTERVAL '1 day', if_not_exists => TRUE);

-- Convert Trades to Hypertable (1-hour chunks)
SELECT create_hypertable('quant.trades', 'timestamp', chunk_time_interval => INTERVAL '1 hour', if_not_exists => TRUE);

-- Convert Orderbook Metrics to Hypertable (6-hour chunks)
SELECT create_hypertable('quant.orderbook_metrics', 'timestamp', chunk_time_interval => INTERVAL '6 hours', if_not_exists => TRUE);

-- Convert Predictions to Hypertable (1-day chunks)
SELECT create_hypertable('quant.predictions', 'prediction_time', chunk_time_interval => INTERVAL '1 day', if_not_exists => TRUE);
```

### Compression Policies
To maximize query performance and reduce storage footprint:
```sql
-- Enable column compression ordered by symbol and timestamp
ALTER TABLE quant.candles SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'symbol,resolution',
    timescaledb.compress_orderby = 'timestamp DESC'
);

-- Compress chunks older than 3 days
SELECT add_compression_policy('quant.candles', INTERVAL '3 days');
```

### Retention Policies
```sql
-- Drop raw execution tick data older than 30 days (aggregated candles are preserved)
SELECT add_retention_policy('quant.trades', INTERVAL '30 days');

-- Drop raw orderbook snapshots older than 14 days
SELECT add_retention_policy('quant.orderbook_snapshots', INTERVAL '14 days');
```
