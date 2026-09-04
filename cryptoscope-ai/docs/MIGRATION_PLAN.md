# CryptoScope AI — Multi-Phase Migration & Rollout Plan

**Step-by-Step Architecture Migration Sequence (Phases 1–12)**  

---

## 1. Migration Sequence & Execution Phases

To ensure zero downtime and maintain application stability, migration proceeds sequentially:

```
Phase 1: Canonical Backend Consolidation
    ├── Isolate legacy/backend/
    └── Unify routing on /api/v1
        │
        ▼
Phase 2: Supabase Auth & JWT Verification
    ├── Deploy services/auth/supabase_verifier.py
    └── Link user profiles via Supabase user UUID
        │
        ▼
Phase 3: PostgreSQL & TimescaleDB Setup
    ├── Apply Alembic schema migrations (product, quant, mlops, audit)
    └── Create hypertables and compression policies
        │
        ▼
Phase 4: Redis Caching & Streams
    ├── Configure key namespaces and stream queues
    └── Enable at-least-once consumer groups
        │
        ▼
Phase 5: Provider Telemetry & Ingestion
    ├── Real Binance USD-M, Bybit V5, OKX Swap workers
    └── Dynamic data-quality scoring gate
        │
        ▼
Phase 6: Online & Offline Feature Store
    ├── Compute point-in-time features in Redis
    └── Parquet historical archives in Cloudflare R2
        │
        ▼
Phase 7: MLflow Registry & Truthful Model Serving
    ├── Register candidate models with artifact manifests
    └── Label heuristic baselines with full transparency
        │
        ▼
Phase 8: Android Client Unification
    ├── Route all screen data through CryptoScopeBackendApiService
    └── Isolate raw exchange fallback calls
        │
        ▼
Phase 9: Firebase FCM & Device Token Management
    ├── Implement POST /api/v1/devices
    └── Dispatch push notifications for signals & alerts
        │
        ▼
Phase 10: Telegram Bot Integration
    ├── Direct bot to canonical /api/v1 routes
    └── Implement /link one-time token authorization
        │
        ▼
Phase 11: Object Storage & Parquet Lake
    ├── Configure R2 / S3 storage service
    └── Schedule daily Parquet partition writes
        │
        ▼
Phase 12: Observability & Production Go-Live
    ├── Prometheus metrics & Grafana dashboards
    └── Continuous synthetic data scanning & test assertions
```

---

## 2. Rollback & Contingency Safeguards

- **Auth Fallback**: The Supabase token verifier supports asymmetric JWKS with symmetric secret fallback.
- **Data Resilience**: If TimescaleDB is undergoing scheduled maintenance, the Redis caching layer serves recent market quotes and predictions.
- **Provider Circuit Breakers**: If an exchange API throttles requests, the aggregator redistributes weights to active healthy venues.
