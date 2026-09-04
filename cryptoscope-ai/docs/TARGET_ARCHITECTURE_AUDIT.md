# CryptoScope AI — Target Architecture Audit

**Subsystem Forensic Classification & Target State Specification**  
**Role**: Principal Software Architect & Quantitative Systems Engineer  
**Date**: September 2026  

---

## 1. Major Subsystem Classification

| Subsystem / Directory | Current Implementation | Target Architectural State | Classification | Migration Action & Justification |
|---|---|---|---|---|
| `app/` (Android Client) | Jetpack Compose M3, Retrofit client pointing to backend `/api/v1` with optional isolated Binance direct calls | Android client talks solely to CryptoScope FastAPI backend behind Cloudflare. Supabase Auth token passed in Authorization header. | **MIGRATE / REFACTOR** | Enforce zero direct exchange calls in production mode. Align with Supabase JWT flow. |
| `cryptoscope-ai/apps/api/` | Canonical FastAPI gateway on `/api/v1`, dynamic provenance, explicit CORS | Production API gateway implementing Supabase verification, market data, predictions, FCM devices, and admin endpoints. | **KEEP / REFACTOR** | Canonical production backend entrypoint. |
| `legacy/backend/` | Obsolete FastAPI server with duplicate endpoints | Fully decommissioned, quarantined in `legacy/backend/` with `NON_PRODUCTION.md`. | **DEPRECATE** | Zero production execution or deployment dependencies. |
| `cryptoscope-ai/database/` | Async SQLAlchemy models, SQLite (dev) / PostgreSQL (prod) | PostgreSQL with partitioned `product`, `quant`, `mlops`, `audit` schemas, TimescaleDB hypertables, and Alembic migrations. | **MIGRATE** | Add product schema with Supabase user UUID foreign identity. |
| `cryptoscope-ai/services/` | Aggregation, predictions, feature engine, orderbook, alerts | Core quant domain services backed by Redis Streams, online feature store, and model serving. | **KEEP / ENHANCE** | Integrate Supabase JWT verification and notification service. |
| `cryptoscope-ai/ml/` | Heuristic baselines + PyTorch research models (`tcn.py`, `patchtst.py`) | Production ML pipeline managed by MLflow model registry with clear artifact lifecycle (`EXPERIMENTAL` $\to$ `PRODUCTION`). | **KEEP / REFACTOR** | Truthful model serving; abstain when models unavailable. |
| `docker/` | Docker Compose definitions | Multi-service compose: API, Ingestion workers, Redis, TimescaleDB, MLflow, Prometheus, Grafana. | **MIGRATE / REFACTOR** | Unified Docker stack supporting local and single-VM production. |

---

## 2. Target Architecture Specification

```
                          ANDROID CLIENT (Compose M3)
                                      │
                                      ▼
                           SUPABASE AUTH GATEWAY
                    (Email/Password, Google OAuth, Tokens)
                                      │
                                      │ Supabase JWT
                                      ▼
                        CLOUDFLARE EDGE & REVERSE PROXY
                         (TLS Termination, DDoS, WAF)
                                      │
                                      ▼
                        FASTAPI PRODUCTION GATEWAY
                     (cryptoscope-ai/apps/api/main.py)
                                      │
       ┌──────────────────────────────┼──────────────────────────────┐
       ▼                              ▼                              ▼
POSTGRESQL / TIMESCALE            REDIS CLUSTER                OBJECT STORAGE
• product.user_profiles         • Market ticker cache         (S3 / R2 / MinIO)
• product.watchlists            • L2 Orderbook cache          • Parquet datasets
• product.alerts                • Online feature cache        • Model artifacts
• product.device_tokens         • Redis Streams (trades, OI)  • Research reports
• quant.candles (hypertable)    • Distributed locks / pubsub  • Historical archives
• quant.predictions (hypertable)
       │                              │                              │
       └──────────────────────────────┼──────────────────────────────┘
                                      │
                   ┌──────────────────┴──────────────────┐
                   ▼                                     ▼
          MLFLOW REGISTRY & MLOPS              NOTIFICATION SERVICES
         • Candidate / Production models      • Firebase FCM (Android push)
         • Scalers & Calibrators              • Telegram Bot Alert Engine
         • Purged Walk-Forward metrics
```

---

## 3. Migration Risks & Mitigation Ledger

1. **Direct Mobile Network Calls**: Direct calls from mobile to exchange endpoints risk rate limiting, API key exposure, and inconsistent state.  
   *Mitigation*: Android routes all requests through `CryptoScopeBackendApiService` (`/api/v1`). Direct exchange calls are isolated and disabled by default.
2. **Auth Drift & Dual Identity**: Storing independent user passwords in FastAPI while using Supabase Auth leads to credential desynchronization.  
   *Mitigation*: Supabase Auth is the sole identity provider. FastAPI verifies Supabase JWTs cryptographically server-side and stores the Supabase UUID as foreign identity.
3. **Database Scalability**: Storing high-frequency tick and delta orderbook data in standard relational tables degrades transaction throughput.  
   *Mitigation*: TimescaleDB hypertables with automatic chunking and retention policies handle time-series data; Redis Streams buffer live tick ingestion.
