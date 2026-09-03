# CryptoScope AI — Repository Current State Audit (Step 0)
**Date:** September 2026  
**Auditor:** Principal Backend & Quant Data Engineer  

---

## 1. Executive Summary & Inventory

An exhaustive inspection of the entire CryptoScope AI repository was conducted across all subsystems:
- `backend/` (FastAPI single-module prototype)
- `cryptoscope-ai/` (FastAPI modular microservice gateway + ML platform)
- `app/` (Android Jetpack Compose application with Retrofit/Moshi client)
- `database/` (SQLAlchemy models and session bindings)
- `providers/` (Exchange connectors and enrichment services)
- `services/` (Aggregators, feature engine, prediction, orderbook, tradeflow)
- `ml/` (Dataset generation, model baselines, calibration, triple barrier labeling)
- `tests/` (Unit and integration test suites)
- Docker & Infrastructure configurations

### Core Findings
1. **Two Competing Backends:** `backend/` (single file `main.py`) and `cryptoscope-ai/` (modular architecture). Neither was fully connected to real live Binance websockets or persistence in production.
2. **Fabricated Fallback Data in Critical Paths:**
   - In `backend/main.py`: Random price walks (`random.uniform(-15.0, 15.0)`), synthetic candles, and mocked order books.
   - In `cryptoscope-ai/providers/exchanges/binance.py`: Completely simulated return values with hardcoded `base_prices = {"BTC": 67450.0, ...}` and artificial candle loops.
   - In `cryptoscope-ai/services/feature_engine.py`: Hardcoded fallbacks (`closes = [67500.0] * 50`, `funding_rate = 0.000105`, `funding_zscore = 0.42`, `meme_sector_dominance_pct = 58.4`).
   - In `cryptoscope-ai/services/prediction.py`: Fabricated price map and 50 duplicated candles on missing data.
   - In `app/src/main/java/com/example/core/data/CryptoScopeRepository.kt`: Random tick jittering (`+ Random.nextDouble(-12.0, 15.0)`).
3. **Mislabeled Machine Learning Models:** Heuristic formulas in `temporal_tft.py`, `orderflow_tcn.py`, and `tabular_expert.py` were branded as deep learning (TFT, TCN, XGBoost) without actual trained weights or artifacts.
4. **Database & Infrastructure Gaps:**
   - Hardcoded SQLite URL (`sqlite+aiosqlite:///./cryptoscope.db`) in `session.py` instead of utilizing `settings.DATABASE_URL`.
   - `docker-compose.yml` referenced nonexistent paths (`infra/docker/api.Dockerfile`, `infra/postgres/init.sql`).
5. **Anti-Leakage Verification:** `anti_leakage_verified = True` was hardcoded in several models rather than verified by point-in-time timestamp checks.

---

## 2. Component-by-Component Classification

| Path / Component | Classification | Description & Current State | Target Action |
|---|---|---|---|
| `backend/main.py` | **DUPLICATED / LEGACY** | Monolithic 824-line prototype with hardcoded mocks and random walks. | Deprecate, mark legacy, re-route contracts to canonical backend. |
| `cryptoscope-ai/apps/api/main.py` | **REAL / PARTIAL** | Master API gateway with canonical JSON envelope and routing. | Standardize to `/api/v1/` canonical routes, add hardened CORS, health checks. |
| `cryptoscope-ai/providers/exchanges/binance.py` | **MOCK** | Fake ticker, candle, depth, and derivatives generator using hardcoded prices. | Replace with genuine async Binance USD-M Futures REST & WS provider. |
| `cryptoscope-ai/providers/exchanges/bybit.py` | **PARTIAL** | Basic structure with mock values. | Keep as secondary provider, mark status cleanly. |
| `cryptoscope-ai/providers/exchanges/additional.py` | **PARTIAL** | OKX, Coinbase, Hyperliquid stub adapters. | Keep as secondary providers with real fallback/unavailability flags. |
| `cryptoscope-ai/providers/base.py` | **REAL** | Strong canonical dataclasses (`CanonicalInstrument`, `CanonicalTicker`, etc.). | Upgrade to Pydantic v2 domain models with strict UTC and timestamp tracking. |
| `cryptoscope-ai/services/feature_engine.py` | **PARTIAL / MOCK** | Comprehensive quantitative formulas, but fallback values were hardcoded fake numbers. | Purge all fake fallbacks; return `DATA_UNAVAILABLE` or `None` on missing data. |
| `cryptoscope-ai/services/prediction.py` | **PARTIAL / MOCK** | Multi-expert ensemble orchestrator; generated fake fallback candles when missing. | Require real inputs; return `MODEL_UNAVAILABLE` / `DATA_UNAVAILABLE`. |
| `cryptoscope-ai/services/orderbook.py` | **REAL** | Microprice, depth, convexity, and OBI calculations. | Integrate sequence validation, gap detection, and resynchronization. |
| `cryptoscope-ai/services/tradeflow.py` | **REAL** | CVD, aggressive buy/sell ratio, whale flow tracking. | Connect to real aggTrade stream. |
| `cryptoscope-ai/services/derivatives.py` | **REAL** | Funding rate, open interest, liquidation tracking logic. | Connect to real Binance USD-M futures metrics. |
| `cryptoscope-ai/services/websocket_manager.py` | **PARTIAL** | Basic WebSocket connection manager. | Upgrade to resilient WebSocket supervisor with heartbeat and reconnect backoff. |
| `cryptoscope-ai/services/registry.py` | **REAL** | Multi-asset registry (BTC, ETH, SOL, DOGE, etc.). | Integrate with real exchange discovery. |
| `cryptoscope-ai/services/resilience.py` | **REAL** | Circuit breaker, rate limiting, and fallback management. | Integrate with provider HTTP engine. |
| `cryptoscope-ai/ml/models/tabular_expert.py` | **MOCK (HEURISTIC)** | Named "Tabular XGBoost" but is a heuristic formula. | Relabel as `HeuristicTabularBaseline` / `EXPERIMENTAL_HEURISTIC`. |
| `cryptoscope-ai/ml/models/orderflow_tcn.py` | **MOCK (HEURISTIC)** | Named "Orderflow TCN" but is a heuristic formula. | Relabel as `HeuristicOrderflowBaseline` / `EXPERIMENTAL_HEURISTIC`. |
| `cryptoscope-ai/ml/models/temporal_tft.py` | **MOCK (HEURISTIC)** | Named "Temporal TFT" but is a heuristic formula. | Relabel as `HeuristicTemporalBaseline` / `EXPERIMENTAL_HEURISTIC`. |
| `cryptoscope-ai/ml/models/meta_ensemble.py` | **REAL / PARTIAL** | Stacking & weighting ensemble logic. | Relabel model types to heuristic baseline until real weights exist. |
| `cryptoscope-ai/ml/labeling/triple_barrier.py` | **REAL** | De Prado triple barrier labeling implementation. | Preserve and verify with automated anti-leakage tests. |
| `cryptoscope-ai/ml/datasets/walk_forward.py` | **REAL** | Purged walk-forward CV generator. | Verify embargo window and chronological separation. |
| `cryptoscope-ai/database/session.py` | **BROKEN / PARTIAL** | Hardcoded SQLite path; ignored `DATABASE_URL`. | Support PostgreSQL+TimescaleDB via `DATABASE_URL` with asyncpg. |
| `cryptoscope-ai/database/models.py` | **REAL** | SQLAlchemy models for candles, orderbook, funding, OI, liquidations. | Add missing TimescaleDB hypertable definitions, indexes, and upsert keys. |
| `cryptoscope-ai/docker-compose.yml` | **BROKEN** | Missing Dockerfiles in `infra/` and hardcoded secrets. | Create Dockerfiles, init SQL, and parameterize credentials via `.env`. |
| `app/src/main/.../CryptoScopeRepository.kt` | **PARTIAL** | Real Retrofit calls to Binance combined with local random price jitter. | Remove random noise, bind to real stream / backend `/api/v1/`. |
| `app/src/main/.../CryptoApiClient.kt` | **REAL** | Clean Retrofit + Moshi setup targeting public endpoints. | Parameterize base URL via BuildConfig / environment. |

---

## 3. Global Fake / Mock / Random Search Findings

1. **`backend/main.py` lines 491-495:**
   Synthetic candlestick generation using `random.uniform(-0.015, 0.02)`.
2. **`backend/main.py` lines 810-817:**
   Real-time WebSocket emitting `random.uniform(-15.0, 15.0)` to fake price changes.
3. **`cryptoscope-ai/providers/exchanges/binance.py` lines 79-80, 106-116, 155-157:**
   Hardcoded base prices ($67,500 BTC, $3,520 ETH, $148.5 SOL) and artificial math loops for OHLCV bars.
4. **`cryptoscope-ai/services/feature_engine.py` lines 34-37, 67-75, 78-91, 112-116:**
   Fabricated fallbacks for closes, orderbook depth ($4.5M), funding rates (0.000105), and meme metrics.
5. **`cryptoscope-ai/services/prediction.py` line 49-55:**
   Fallback price dictionary and fabrication of 50 uniform candles.
6. **`app/src/main/java/.../CryptoScopeRepository.kt` lines 95-98:**
   `Random.nextDouble(-12.0, 15.0)` simulated jitter in live price loop.

---

## 4. Conclusion & Action Plan
All mock generators and random noise loops are documented and prioritized for systematic replacement by:
1. Canonicalizing `cryptoscope-ai/` as the single production backend.
2. A real asynchronous Binance USD-M Futures REST & WebSocket provider.
3. A robust HTTP engine with rate-limit tracking, retry backoff, and circuit breakers.
4. A WebSocket supervisor with sequence validation and gap-triggered resynchronization.
5. PostgreSQL/TimescaleDB persistence with Alembic migrations.
6. Strict anti-leakage checks and truthful ML baseline labeling.
