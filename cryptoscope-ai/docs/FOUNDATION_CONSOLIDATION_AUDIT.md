# CryptoScope AI — Foundation Consolidation Audit

**Audit Date**: 2026-09-04  
**Auditor**: Principal Software Architect & QA Engineering Team  
**Directive**: Establish single production architecture (Android → Supabase Auth → FastAPI Canonical Backend → PostgreSQL/TimescaleDB + Redis → Providers/ML).

---

## 1. Executive Summary

A full forensic audit was conducted across `app/`, `backend/`, and `cryptoscope-ai/`. Multiple overlapping backend structures, duplicate API prefixes (`/v1` vs `/api/v1`), and scattered mock values were identified. This audit classifies every major subsystem according to the required standard classifications:
`CANONICAL`, `LEGACY`, `DUPLICATE`, `PARTIAL`, `BROKEN`, `MOCK`, `DEAD`, `TEST_ONLY`.

---

## 2. Subsystem Classification Matrix

| Subsystem | Path / Component | Classification | Description & Action |
|:---|:---|:---|:---|
| **API Gateway (Production)** | `cryptoscope-ai/apps/api/` | `CANONICAL` | The sole production entry point. Needs modular router split (`lifespan.py`, `dependencies.py`, `routers/*`). |
| **Legacy Backend** | `legacy/backend/` | `LEGACY` | Deprecated standalone prototype backend. Runtime entry points disabled. Kept in `legacy/backend/` for historical reference. |
| **Adapter Router** | `cryptoscope-ai/api/v1_router.py` | `DUPLICATE` / `PARTIAL` | Overlaps with `apps/api/main.py`. Consolidated into modular routers under `apps/api/routers/`. |
| **Authentication Identity** | Supabase Auth (`supabase_verifier.py`) | `CANONICAL` | Identity provider for mobile client. Verifies JWT (signature, expiry, issuer, subject) server-side. |
| **FastAPI Legacy Auth** | `backend/auth/` | `DEAD` | Deprecated local password-hashing DB. Supabase Auth is canonical identity authority. |
| **Database Engine** | PostgreSQL + TimescaleDB (`database/session.py`) | `CANONICAL` | Production DB engine configured via `DATABASE_URL`. SQLite explicitly restricted to dev/test fallback. |
| **Database Schema** | `product`, `quant`, `mlops`, `audit` | `CANONICAL` | Multi-schema architecture. Quant time-series tables converted to TimescaleDB hypertables. |
| **Database Migrations** | `cryptoscope-ai/database/migrations/` | `CANONICAL` | Alembic-driven migrations. Replaces ad-hoc `create_all()` in production. |
| **Cache & State Store** | Redis (`core/redis.py`) | `CANONICAL` | Standardized key contracts (`ticker:{p}:{s}`, `oi:{p}:{s}`, etc.), TTL, source freshness. |
| **Android Backend Client** | `CryptoScopeBackendApiService` / `CryptoApiClient` | `CANONICAL` | Single backend client targeting `BuildConfig.BACKEND_BASE_URL` with Auth Interceptor for protected routes. |
| **Android Direct Exchange** | `CryptoFuturesApiService` (Binance direct) | `LEGACY` / `DEAD` | Direct exchange network calls from Android client deprecated and removed from release builds. |
| **Exchange Provider (Binance)**| `cryptoscope-ai/providers/binance.py` | `CANONICAL` | Canonical market provider. Ingests ticker, orderbook depth, trades, funding, and OI. |
| **Provider Health Engine** | `services/resilience.py` & `routers/providers.py` | `CANONICAL` | Real health status (`HEALTHY`, `DEGRADED`, `STALE`, `DOWN`, `NOT_CONFIGURED`). No hardcoded status. |
| **Data Quality Gate** | `services/data_quality.py` | `CANONICAL` | Deterministic computation based on latency, completeness, and freshness. |
| **ML Inference Engine** | `services/prediction.py` & `ml/` | `CANONICAL` | Deep learning models (LSTM, PatchTST, DeepAR) with quantile bounds and feature store integration. |
| **Notification Service** | `services/notifications/` | `CANONICAL` | FCM push notifications and Telegram alerts. |
| **Object Storage Service** | `services/object_storage.py` | `CANONICAL` | Multi-cloud S3/R2/MinIO storage for model weights and historical tick data. |
| **Container Stack** | `docker-compose.yml` | `CANONICAL` | Consolidated stack: `api`, `postgres` (TimescaleDB), `redis`. |

---

## 3. Data Integrity & Mock Removal Audit

1. **Hardcoded Formatted Strings**: Discovered hardcoded placeholders (e.g. `"$106.9B"` OI) in helper functions. Replaced with dynamic computation or `DATA_UNAVAILABLE` envelope.
2. **Deterministic Fallbacks**: Missing metrics now strictly return HTTP 200 with `status: "DATA_UNAVAILABLE"` or appropriate error envelopes rather than fabricated pseudo-metrics.
3. **Anti-Leakage Invariant**: Verified strictly: `feature_time <= prediction_time`.
