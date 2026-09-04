# CryptoScope AI — Android API Client Matrix

**Purpose**: Exhaustive inventory of all mobile network clients, Retrofit services, endpoints, data sources, and persistence mappers.  
**Auditor**: Senior Android / Kotlin Architecture Engineer  
**Canonical Base URL**: `BuildConfig.BACKEND_BASE_URL` (Defaults to `http://10.0.2.2:8000/` for emulator, configurable via `activeBackendUrl`)  

---

## 1. Network Client & Endpoint Ledger

| Client / Class | Base URL / Connection | Endpoint Route | Purpose & UI Consumer | Backend / Provider | Auth Required? | Decision / Action |
|---|---|---|---|---|---|---|
| `CryptoScopeBackendApiService` | `CryptoApiClient.activeBackendUrl` | `GET api/v1/market/overview` | Global aggregated market metrics, OI, volume, and sentiment for HomeScreen | Canonical FastAPI | No | **KEEP** (Primary institutional header) |
| `CryptoScopeBackendApiService` | `CryptoApiClient.activeBackendUrl` | `GET api/v1/sentiment/fear-greed` | Fear & Greed index historical series for FearAndGreedScreen | Canonical FastAPI | No | **KEEP** (Institutional sentiment) |
| `CryptoScopeBackendApiService` | `CryptoApiClient.activeBackendUrl` | `GET api/v1/etf/overview` | Institutional Bitcoin & Ethereum ETF flows for ETF / Macro screens | Canonical FastAPI | No | **KEEP** (Institutional flow telemetry) |
| `CryptoScopeBackendApiService` | `CryptoApiClient.activeBackendUrl` | `GET api/v1/rankings` | 24h volume, gainers, losers, and OI ranking table for RankingScreen | Canonical FastAPI | No | **KEEP** (Market sorting) |
| `CryptoScopeBackendApiService` | `CryptoApiClient.activeBackendUrl` | `GET api/v1/screener` | Multi-parameter contract screener for MarketsScreen | Canonical FastAPI | No | **KEEP** (Real-time screening) |
| `CryptoScopeBackendApiService` | `CryptoApiClient.activeBackendUrl` | `GET api/v1/radar/contracts` | High-frequency abnormal volume and OI surge alerts for HomeScreen banner | Canonical FastAPI | No | **KEEP** (High-priority intelligence) |
| `CryptoScopeBackendApiService` | `CryptoApiClient.activeBackendUrl` | `GET api/v1/predictions/{symbol}` | Multi-horizon forecast (P10-P90, direction, confidence, SHAP) for AIPredictionScreen | Canonical FastAPI | No | **KEEP** (Primary predictive AI) |
| `CryptoScopeBackendApiService` | `CryptoApiClient.activeBackendUrl` | `GET api/v1/news` | Real-time filtered market news and regulatory events for NewsScreen | Canonical FastAPI | No | **KEEP** (Macro intelligence) |
| `CryptoScopeBackendApiService` | `CryptoApiClient.activeBackendUrl` | `GET api/v1/events` | Economic calendar releases, FOMC, CPI for MacroScreen | Canonical FastAPI | No | **KEEP** (Macro events) |
| `CryptoScopeBackendApiService` | `CryptoApiClient.activeBackendUrl` | `GET api/v1/providers/status` | Real-time exchange node latency, error rates, and circuit breaker status for SystemHealthScreen | Canonical FastAPI | No | **KEEP** (SRE / node observability) |
| `CryptoFuturesApiService` | `https://fapi.binance.com/` | `GET fapi/v1/ticker/24hr` | Direct low-latency fallback for raw exchange ticker prices | Public Binance USD-M | No | **KEEP AS ISOLATED FALLBACK** (Raw exchange mode only) |
| `CryptoFuturesApiService` | `https://fapi.binance.com/` | `GET fapi/v1/klines` | Direct low-latency fallback for raw candlestick chart series | Public Binance USD-M | No | **KEEP AS ISOLATED FALLBACK** (Offline / raw mode) |
| `CryptoFuturesApiService` | `https://fapi.binance.com/` | `GET fapi/v1/depth` | Direct low-latency fallback for raw L2 orderbook ladder | Public Binance USD-M | No | **KEEP AS ISOLATED FALLBACK** (Raw mode only) |
| `CryptoFuturesApiService` | `https://fapi.binance.com/` | `GET fapi/v1/openInterest` | Direct low-latency fallback for contract open interest | Public Binance USD-M | No | **KEEP AS ISOLATED FALLBACK** (Raw mode only) |
| `CryptoFuturesApiService` | `https://fapi.binance.com/` | `GET fapi/v1/premiumIndex` | Direct low-latency fallback for funding rate & mark price | Public Binance USD-M | No | **KEEP AS ISOLATED FALLBACK** (Raw mode only) |
| `CryptoFuturesApiService` | `https://fapi.binance.com/` | `GET fapi/v1/trades` | Direct low-latency fallback for real-time market trade tape | Public Binance USD-M | No | **KEEP AS ISOLATED FALLBACK** (Raw mode only) |

---

## 2. Architectural Boundaries & Data Isolation Rules

1. **Strict Client Separation**: The Android application maintains two cleanly separated data source abstractions:
   - `CryptoScopeBackendRemoteDataSource`: Communicates with `CryptoScopeBackendApiService` for all consolidated AI predictions, multi-venue orderflow, sentiment, and system health.
   - `FuturesRemoteDataSource`: Connects directly to public Binance USD-M for optional raw exchange telemetry, preventing single-point failure if the backend gateway is undergoing maintenance.
2. **Room Database Integration**: `CryptoScopeRepository` coordinates cache-first reads and background refreshes via Room (`CryptoScopeDatabase`), persisting tickers, user watchlist, alerts, and paper trades with full offline capability.
