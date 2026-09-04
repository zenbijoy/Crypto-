# CryptoScope AI — Redis & Streams Architecture

**Cache Invalidation, Key Schemas, Pub/Sub & Stream Consumer Groups**  

---

## 1. Canonical Key Hierarchy

All Redis keys adhere to a strict hierarchical namespace:

| Key Pattern | Data Structure | TTL | Purpose |
|---|---|---|---|
| `market:ticker:{provider}:{symbol}` | Hash / String JSON | 10 seconds | Latest 24hr quote, last price, bid/ask |
| `market:mark:{provider}:{symbol}` | String (Float) | 10 seconds | Mark price & index price for derivatives |
| `market:funding:{provider}:{symbol}` | Hash | 60 seconds | Current funding rate, predicted rate, basis |
| `market:oi:{provider}:{symbol}` | String (Float) | 30 seconds | Open interest in USD and base contracts |
| `orderbook:{provider}:{symbol}` | Hash (Bids/Asks JSON) | 5 seconds | Top 50 levels L2 depth ladder |
| `feature:{symbol}:{horizon}:{version}` | Hash | 5 minutes | Online feature store vector for live inference |
| `prediction:{symbol}:{horizon}` | Hash | 60 seconds | Latest ensemble probabilistic prediction payload |
| `provider:health:{provider}` | Hash | 30 seconds | Ping latency, error rate, circuit state |
| `rate_limit:{ip_or_user_id}` | String Counter | 60 seconds | Leaky-bucket / sliding-window rate limit state |

---

## 2. Redis Streams Topology

High-throughput market events are published to dedicated Redis Streams and ingested asynchronously by consumer groups:

```
[ Ingestion Workers ]
        │
        ├──> stream:trades       ──> [ Trade Aggregation Worker ]
        ├──> stream:candles      ──> [ Multi-Timeframe Builder ]
        ├──> stream:orderbook    ──> [ Orderbook Sync & OBI Engine ]
        ├──> stream:funding      ──> [ Derivatives Service ]
        ├──> stream:oi           ──> [ Open Interest Monitor ]
        ├──> stream:features     ──> [ Online Feature Store ]
        └──> stream:predictions  ──> [ WebSocket Pub/Sub & FCM Dispatcher ]
```

### Consumer Group Guarantees
- **At-least-once delivery**: Explicit `XACK` upon successful batch processing.
- **Dead-Letter Queue (DLQ)**: Events exceeding 3 retries or parsing failures are routed to `stream:dlq:events` for inspection.
- **Lag Monitoring**: Metric `redis_stream_lag_records` tracks consumer group pending offsets.
