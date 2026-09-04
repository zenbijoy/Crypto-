# CryptoScope AI — Current Architecture Map & Runtime Paths

**Classification**: Architecture Dataflow Specification & Subsystem Mapping  
**Canonical Backend**: `cryptoscope-ai/`  
**Legacy Backend Status**: Deprecated and quarantined in `legacy/backend/` (`NON_PRODUCTION.md`)  
**Canonical API Prefix**: `/api/v1`  

---

## 1. End-to-End Production Runtime Dataflow

The unified architecture follows a strict, unidirectional dataflow from external quantitative exchanges down to the client presentation layers:

```
                  ┌────────────────────────────────────────────────────────┐
                  │          EXTERNAL QUANTITATIVE DATA VENUES             │
                  │   Binance USD-M  •  Bybit Linear V5  •  OKX Swap V5    │
                  │   CoinGecko  •  DefiLlama  •  CoinMetrics  •  Macro    │
                  └───────────────────────────┬────────────────────────────┘
                                              │ Real HTTPS / WSS
                                              ▼
                  ┌────────────────────────────────────────────────────────┐
                  │             EXCHANGE INGESTION LAYER                   │
                  │  providers/exchanges/binance.py (Real public REST/WS)  │
                  │  providers/exchanges/bybit.py (Real linear tickers/OI) │
                  │  providers/exchanges/okx.py (Real swap orderbook/depth)│
                  │  InstrumentRegistry: Canonical symbol resolver        │
                  └───────────────────────────┬────────────────────────────┘
                                              │ Point-in-time timestamped
                                              ▼
                  ┌────────────────────────────────────────────────────────┐
                  │             DATA QUALITY & RECTIFICATION               │
                  │  services/data_quality.py (Dynamic freshness check)    │
                  │  Rejects stale data, validates sequence integrity      │
                  │  Status: HEALTHY / DEGRADED / STALE / REJECTED         │
                  └───────────────────────────┬────────────────────────────┘
                                              │ Validated Events
                                              ▼
                  ┌────────────────────────────────────────────────────────┐
                  │             FEATURE COMPUTATION ENGINE                 │
                  │  services/feature_engine.py (Point-in-time invariants) │
                  │  OBI, Microprice, CVD, Funding Z-score, Volatility     │
                  │  Anti-leakage: feature_time <= prediction_time         │
                  └───────────────────────────┬────────────────────────────┘
                                              │ Feature Vectors
                                              ▼
                  ┌────────────────────────────────────────────────────────┐
                  │           CANONICAL PREDICTION & ML ENGINE             │
                  │  services/prediction.py                                │
                  │  ├── HeuristicTabularBaseline (RSI, MACD, Skew)        │
                  │  ├── HeuristicOrderflowBaseline (OBI, CVD, Microprice) │
                  │  ├── HeuristicTemporalBaseline (Multi-horizon decay)   │
                  │  └── LearnedMixtureOfExperts (Regime-aware gating)     │
                  │  Enforces: probabilities sum to 1.0                    │
                  │  Enforces: NO_TRADE => actionable = false              │
                  └───────────────────────────┬────────────────────────────┘
                                              │
                      ┌───────────────────────┴───────────────────────┐
                      ▼                                               ▼
     ┌───────────────────────────────────┐           ┌───────────────────────────────────┐
     │      PERSISTENCE & STATE          │           │       CANONICAL API GATEWAY       │
     │  PostgreSQL/TimescaleDB (Prod)    │           │  cryptoscope-ai/apps/api/main.py  │
     │  SQLite (Local dev/testing)       │           │  Prefix: /api/v1                  │
     │  Redis Streams / Cache            │           │  Explicit CORS (Zero wildcard)    │
     │  Alembic Migrations               │           │  Real response provenance         │
     └───────────────────────────────────┘           └─────────────────┬─────────────────┘
                                                                       │
                                      ┌────────────────────────────────┴────────────────────────────────┐
                                      ▼                                                                 ▼
                     ┌───────────────────────────────────┐                             ┌───────────────────────────────────┐
                     │          ANDROID CLIENT           │                             │        TELEGRAM INTELLIGENCE      │
                     │  CryptoScopeBackendApiService     │                             │  apps/telegram/bot.py             │
                     │  CryptoScopeRepository            │                             │  Real-time /predict command       │
                     │  CryptoViewModel (Zero fake data) │                             │  Consumes canonical /api/v1       │
                     │  Room Database (Offline caching)  │                             │  Alert triggers on threshold      │
                     │  Jetpack Compose M3 UI Screens    │                             │  Zero fake forecasting            │
                     └───────────────────────────────────┘                             └───────────────────────────────────┘
```

---

## 2. Forensic Comparison: Legacy `backend/` vs Canonical `cryptoscope-ai/`

| Subsystem Domain | Legacy Path (`legacy/backend/`) | Canonical Path (`cryptoscope-ai/`) | Architectural Reconciliation |
|---|---|---|---|
| **Production Runtime** | `backend/main.py` (Deprecated) | `cryptoscope-ai/apps/api/main.py` | **One Canonical Backend**. Legacy moved to `legacy/backend/` with `NON_PRODUCTION.md`. |
| **API Prefix** | `/v1/...` | `/api/v1/...` | Unified to `/api/v1`. Android and Telegram call only `/api/v1`. |
| **Authentication** | Basic dictionary mock in `backend/main.py` | Canonical JWT auth in `cryptoscope-ai/apps/api/main.py` | Unified on canonical JWT token lifecycle and user profile state. |
| **Market Tickers** | Static price fallbacks | Real Binance/Bybit public REST in `providers/exchanges/` | 100% real exchange data with timestamps and source provenance. |
| **Predictions** | Random uniform number generation | Deterministic feature engine + `LearnedMixtureOfExperts` | Real quant models with probability normalization and uncertainty. |
| **Paper Trading** | Ephemeral memory dictionary | Persistent `paper_trading_engine` with balance tracking | Real trade journaling, balance updates, and mark-to-market PnL. |
| **Alerts Engine** | In-memory queue | `alert_engine` with threshold evaluations and webhooks | Unified alert dispatch based on live market conditions. |
| **WebSocket** | Ad-hoc multiplexer | `ws_manager` in `services/websocket_manager.py` | Standardized channel subscriptions (ticker, depth, predictions). |
| **Model Registry** | Hardcoded champion string | Registry with EXPERIMENTAL, CANDIDATE, PRODUCTION stages | Models strictly declared; heuristic baselines explicitly labeled. |

---

## 3. Duplication Resolution Summary

1. **Server Isolation**: No dual FastAPI processes run in production. `legacy/backend/` is marked `NON_PRODUCTION` and omitted from Docker compose and deployment targets.
2. **Client Convergence**: Android network client points solely to the canonical gateway via `CryptoApiClient.activeBackendUrl` (`/api/v1`).
3. **Bot Convergence**: Telegram bot queries the canonical `/api/v1` routes exclusively.
