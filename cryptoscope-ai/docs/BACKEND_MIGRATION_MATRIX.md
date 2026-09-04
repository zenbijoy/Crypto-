# CryptoScope AI — Backend Migration Matrix

**Purpose**: Systematic mapping and decommissioning of legacy routes into the canonical API gateway  
**Canonical Server**: `cryptoscope-ai/apps/api/main.py`  
**Legacy Server**: `legacy/backend/main.py` (Decommissioned)  
**Target Canonical Prefix**: `/api/v1`  

---

## 1. Migration Ledger

| Legacy Endpoint (`legacy/backend/main.py`) | Canonical Endpoint (`cryptoscope-ai/apps/api/main.py`) | Status | Consumer | Migration Completed | Notes |
|---|---|---|---|---|---|
| `GET /v1/health` | `GET /api/v1/health` | **MIGRATED** | Ops, Android, Telegram | Yes | Live/Ready health status checking dependencies |
| `POST /v1/auth/login` | `POST /api/v1/auth/login` | **MIGRATED** | Android UI, Web Client | Yes | Replaced mock dictionary with JWT token auth |
| `POST /v1/auth/register` | `POST /api/v1/auth/register` | **MIGRATED** | Android UI | Yes | User persistence with password hashing |
| `GET /v1/auth/me` | `GET /api/v1/auth/me` | **MIGRATED** | Android User Center | Yes | Canonical profile response |
| `GET /v1/market/overview` | `GET /api/v1/market/overview` | **MIGRATED** | Android Home Screen | Yes | Live aggregated OI, volume, and sentiment |
| `GET /v1/tickers` | `GET /api/v1/market/tickers` | **MIGRATED** | Android Markets Screen | Yes | Live multi-venue aggregated tickers |
| `GET /v1/ticker/{symbol}` | `GET /api/v1/market/ticker/{symbol}` | **MIGRATED** | Android Asset Detail | Yes | Real Binance/Bybit market telemetry |
| `GET /v1/candles/{symbol}` | `GET /api/v1/market/candles/{symbol}` | **MIGRATED** | Android Chart Terminal | Yes | Real OHLCV klines across multi-timeframes |
| `GET /v1/orderbook/{symbol}` | `GET /api/v1/market/orderbook/{symbol}` | **MIGRATED** | Android OrderBook Screen | Yes | Validated L2 depth and microprice |
| `GET /v1/trades/{symbol}` | `GET /api/v1/market/trades/{symbol}` | **MIGRATED** | Android Asset Detail | Yes | Real-time recent trade aggregations |
| `GET /v1/derivatives/{symbol}` | `GET /api/v1/derivatives/{symbol}` | **MIGRATED** | Android Derivatives | Yes | Funding rate, open interest, and basis |
| `GET /v1/liquidations` | `GET /api/v1/derivatives/liquidations` | **MIGRATED** | Android Liquidations Screen | Yes | Liquidation heatmap and map estimates |
| `GET /v1/predictions/{symbol}` | `GET /api/v1/predictions/{symbol}` | **MIGRATED** | Android AI Prediction, Telegram | Yes | Probabilities sum to 1.0, NO_TRADE invariant |
| `GET /v1/models` | `GET /api/v1/models` | **MIGRATED** | Android Model Performance | Yes | Real model registry with baseline disclosure |
| `GET /v1/sentiment/fear-greed`| `GET /api/v1/sentiment/fear-greed`| **MIGRATED** | Android Fear & Greed Screen | Yes | Alternative.me real live index |
| `GET /v1/macro` | `GET /api/v1/macro` | **MIGRATED** | Android Macro Screen | Yes | Real macro dominance and economic data |
| `GET /v1/onchain` | `GET /api/v1/onchain` | **MIGRATED** | Android OnChain Screen | Yes | Real on-chain metrics and flow analytics |
| `GET /v1/paper/portfolio` | `GET /api/v1/paper/portfolio` | **MIGRATED** | Android Paper Dashboard | Yes | Persistent paper trading portfolio |
| `POST /v1/paper/order` | `POST /api/v1/paper/order` | **MIGRATED** | Android Paper Order Ticket | Yes | Validated paper execution with slippage |
| `GET /v1/alerts` | `GET /api/v1/alerts` | **MIGRATED** | Android Alerts Screen | Yes | Live user-configured price and metric alerts |
| `POST /v1/alerts` | `POST /api/v1/alerts` | **MIGRATED** | Android Create Alert | Yes | Alert rule registration |
| `GET /v1/providers/status` | `GET /api/v1/providers/status` | **MIGRATED** | Android System Health | Yes | Dynamic latency, error rate, and circuit breakers |
| `WS /v1/ws` | `WS /api/v1/ws` | **MIGRATED** | Android Realtime, Telegram | Yes | Channel multiplexing (tickers, book, signals) |

---

## 2. Decommissioning Verification

1. `legacy/backend/` has been stripped of any production deployment scripts.
2. `NON_PRODUCTION.md` is present in `legacy/backend/` explicitly stating this codebase is not for production use.
3. All Android Retrofit endpoints (`CryptoScopeBackendApiService.kt`) use `/api/v1` routes exclusively.
4. Telegram bot (`apps/telegram/bot.py`) targets the `/api/v1` prefix.
