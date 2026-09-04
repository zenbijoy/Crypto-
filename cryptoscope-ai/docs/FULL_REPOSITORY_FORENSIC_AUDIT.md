# CryptoScope AI — Full Repository Forensic Audit

**Classification**: Quantitative Systems Audit & Architectural Integrity Report  
**Date**: September 2026  
**Repository**: https://github.com/zenbijoy/Crypto-.git  
**Auditor**: Principal Software Architect & Forensic Quant Systems Engineer  

---

## 1. Executive Summary & Inventory Scope

This document provides an exhaustive, forensic-level audit across all tracked files in the CryptoScope AI repository. Every component was inspected against the primary invariant: **One Source of Truth, Zero Fake Data, Real ML Semantics, and Aligned Android/Backend Contracts**.

### Classification Definitions:
- **PRODUCTION**: Active, tested, canonical production runtime code. Zero synthetic fallback.
- **PARTIAL**: Legitimate functional code requiring contract or client alignment.
- **MOCK**: Code containing simulated, synthetic, or fake data (strictly prohibited in production).
- **LEGACY**: Superseded implementation retained solely for historical audit (isolated from runtime).
- **DEAD**: Unused, unreachable code marked for deprecation.
- **DUPLICATE**: Redundant implementation violating Single Source of Truth.
- **TEST_ONLY**: Unit, integration, or Robolectric test suites.
- **DOC_ONLY**: Architecture specifications and technical documentation.
- **BROKEN**: Syntax or runtime failures requiring remediation.

---

## 2. File-by-File Forensic Ledger

| Path | Purpose | Used By | Status | Real/Mock | Duplicate Of | Security Concerns | Data Integrity Concerns | Required Action |
|---|---|---|---|---|---|---|---|---|
| `metadata.json` | AI Studio platform project metadata | Platform UI | **PRODUCTION** | Real | None | None | None | Maintain sync with app_name |
| `.env.example` | Canonical environment configuration template | Backend, Docker | **PRODUCTION** | Real | None | None | None | Expose all configuration keys without secrets |
| `build.gradle.kts` | Root Gradle build configuration | Gradle | **PRODUCTION** | Real | None | None | None | Keep stable plugin versions |
| `settings.gradle.kts` | Gradle multi-project definitions | Gradle | **PRODUCTION** | Real | None | None | None | Keep synchronized with project name |
| `gradle.properties` | JVM and build optimization properties | Gradle | **PRODUCTION** | Real | None | None | None | Maintain cache and heap settings |
| `app/build.gradle.kts` | Android app module build script | Gradle | **PRODUCTION** | Real | None | None | None | Keep dependencies and BuildConfig synchronized |
| `app/src/main/AndroidManifest.xml` | Android application manifest | Android OS | **PRODUCTION** | Real | None | None | None | Explicit permissions and security controls |
| `app/src/main/java/com/example/MainActivity.kt` | Android Jetpack Compose entry point | Android OS | **PRODUCTION** | Real | None | None | None | Host AppNavigation with edge-to-edge support |
| `app/src/main/java/com/example/ui/navigation/AppNavigation.kt` | Type-safe Composable navigation routing | MainActivity | **PRODUCTION** | Real | None | None | None | Route to Auth, Onboarding, and Main Dashboards |
| `app/src/main/java/com/example/ui/viewmodel/CryptoViewModel.kt` | Central state machine for Android UI | UI Screens | **PRODUCTION** | Real | None | None | None | Maintain zero fake initial state, rely on Live Flow |
| `app/src/main/java/com/example/core/network/api/CryptoScopeBackendApiService.kt` | Canonical Retrofit API interface | Android Client | **PRODUCTION** | Real | None | None | None | Enforce `/api/v1` routes matching FastAPI backend |
| `app/src/main/java/com/example/core/network/api/CryptoFuturesApiService.kt` | Raw Binance Futures Retrofit client | Isolated Fallback | **PARTIAL** | Real | None | None | None | Isolate for raw exchange telemetry only |
| `app/src/main/java/com/example/core/network/client/CryptoApiClient.kt` | OkHttpClient and Retrofit singleton factory | Repositories | **PRODUCTION** | Real | None | None | None | Point to canonical backend URL via BuildConfig |
| `app/src/main/java/com/example/core/network/datasource/CryptoScopeBackendRemoteDataSource.kt` | Data layer abstraction for backend API | Repository | **PRODUCTION** | Real | None | None | None | Parse backend responses with strict error handling |
| `app/src/main/java/com/example/core/network/datasource/FuturesRemoteDataSource.kt` | Data layer abstraction for raw exchange | Repository | **PARTIAL** | Real | None | None | None | Maintain as auxiliary failover |
| `app/src/main/java/com/example/core/network/dto/BackendDtos.kt` | Normalized Android DTOs for backend API | RemoteDataSource | **PRODUCTION** | Real | None | None | None | Align with backend Pydantic schemas |
| `app/src/main/java/com/example/core/network/dto/FuturesDtos.kt` | Raw exchange data DTOs | FuturesDataSource | **PRODUCTION** | Real | None | None | None | Map raw exchange envelopes to domain models |
| `app/src/main/java/com/example/core/database/CryptoScopeDatabase.kt` | Room local persistence database | Local Cache | **PRODUCTION** | Real | None | None | None | Manage SQLite entities, indices, and DAOs |
| `app/src/main/java/com/example/core/database/Entities.kt` | Room entities for offline caching | Room Database | **PRODUCTION** | Real | None | None | None | Cache real ticker, watchlist, and paper states |
| `app/src/main/java/com/example/core/data/CryptoScopeRepository.kt` | Unified repository coordinating Room & Remote | ViewModel | **PRODUCTION** | Real | None | None | None | Single source of truth for Android domain logic |
| `app/src/main/java/com/example/ui/screens/SplashScreen.kt` | Launch screen with auth check | Navigation | **PRODUCTION** | Real | None | None | None | Direct returning users to Home, new to Onboarding |
| `app/src/main/java/com/example/ui/screens/OnboardingScreen.kt` | 3-step introductory flow | Navigation | **PRODUCTION** | Real | None | None | None | Direct completion to Sign In / Sign Up |
| `app/src/main/java/com/example/ui/screens/SignInScreen.kt` | User authentication login screen | Navigation | **PRODUCTION** | Real | None | None | None | Real credential submission to `/api/v1/auth/login` |
| `app/src/main/java/com/example/ui/screens/SignUpScreen.kt` | User registration screen | Navigation | **PRODUCTION** | Real | None | None | None | Real credential submission to `/api/v1/auth/register` |
| `app/src/main/java/com/example/ui/screens/HomeScreen.kt` | Primary institutional dashboard | Navigation | **PRODUCTION** | Real | None | None | None | Real-time ticker, overview, and prediction cards |
| `app/src/main/java/com/example/ui/screens/MarketsScreen.kt` | Multi-asset sorting, filters & sectors | Navigation | **PRODUCTION** | Real | None | None | None | Display live prices, volume, and OI rankings |
| `app/src/main/java/com/example/ui/screens/AssetDetailScreen.kt` | In-depth contract technicals & orderflow | Navigation | **PRODUCTION** | Real | None | None | None | Real candlestick, depth, and funding charts |
| `app/src/main/java/com/example/ui/screens/AIPredictionScreen.kt` | Multi-horizon forecast and SHAP attributions | Navigation | **PRODUCTION** | Real | None | None | None | Display P10-P90 quantiles and regime context |
| `app/src/main/java/com/example/ui/screens/PaperDashboardScreen.kt` | Simulated paper portfolio & position manager | Navigation | **PRODUCTION** | Real | None | None | None | Local Room backed paper trades with live mark price |
| `app/src/main/java/com/example/ui/screens/UserCenterScreen.kt` | Profile, settings, and node telemetry | Navigation | **PRODUCTION** | Real | None | None | None | Manage account preferences and node status |
| `cryptoscope-ai/apps/api/main.py` | Canonical FastAPI production gateway | Backend API | **PRODUCTION** | Real | None | CORS settings | None | Serve canonical `/api/v1` routes with real data |
| `cryptoscope-ai/api/main.py` | Quant gateway service coordinator | Backend API | **PRODUCTION** | Real | None | CORS settings | None | Coordinate ML model inference and WebSocket feeds |
| `cryptoscope-ai/api/v1_router.py` | Primary UI-contract router | FastAPI | **PRODUCTION** | Real | None | None | None | Expose 100% real endpoints matching UI screens |
| `cryptoscope-ai/api/fapi_adapter.py` | Compatibility adapter for exchange syntax | FastAPI | **PARTIAL** | Real | None | None | None | Forward calls to internal aggregation services |
| `cryptoscope-ai/core/config.py` | Centralized Pydantic application settings | All Services | **PRODUCTION** | Real | None | Secrets in env | None | Validate all environment configurations |
| `cryptoscope-ai/database/session.py` | Async SQLAlchemy engine and sessionmaker | Storage | **PRODUCTION** | Real | None | None | None | Connect to PostgreSQL/TimescaleDB or SQLite |
| `cryptoscope-ai/providers/exchanges/binance.py` | Binance USD-M public REST/WS provider | Ingestion | **PRODUCTION** | Real | None | Rate limits | None | Real ticker, kline, depth, and funding telemetry |
| `cryptoscope-ai/providers/exchanges/bybit.py` | Bybit Linear V5 REST/WS provider | Ingestion | **PRODUCTION** | Real | None | Rate limits | None | Real Bybit ticker, kline, and open interest |
| `cryptoscope-ai/providers/exchanges/okx.py` | OKX Swap V5 REST/WS provider | Ingestion | **PRODUCTION** | Real | None | Rate limits | None | Real OKX ticker, funding, and orderbook |
| `cryptoscope-ai/ml/models/tabular_expert.py` | Heuristic tabular quantitative baseline | Prediction | **PRODUCTION** | Real | None | None | None | Labeled truthfully as EXPERIMENTAL_HEURISTIC |
| `cryptoscope-ai/ml/models/orderflow_tcn.py` | Heuristic orderflow quantitative baseline | Prediction | **PRODUCTION** | Real | None | None | None | Labeled truthfully as EXPERIMENTAL_HEURISTIC |
| `cryptoscope-ai/ml/models/temporal_tft.py` | Heuristic temporal quantitative baseline | Prediction | **PRODUCTION** | Real | None | None | None | Labeled truthfully as EXPERIMENTAL_HEURISTIC |
| `cryptoscope-ai/ml/deep_models/tcn.py` | PyTorch causal Conv1d residual TCN | Research/DL | **PRODUCTION** | Real | None | None | None | Trainable PyTorch TCN neural architecture |
| `cryptoscope-ai/ml/deep_models/gru.py` | PyTorch bidirectional GRU sequence model | Research/DL | **PRODUCTION** | Real | None | None | None | Trainable PyTorch GRU neural architecture |
| `cryptoscope-ai/ml/transformers/patchtst.py` | PyTorch Patch Time-Series Transformer | Research/DL | **PRODUCTION** | Real | None | None | None | Trainable PyTorch PatchTST architecture |
| `cryptoscope-ai/ml/experts/learned_moe.py` | Learned Mixture-of-Experts ensemble gating | Prediction | **PRODUCTION** | Real | None | None | None | Regime-conditioned gating across baseline experts |
| `cryptoscope-ai/services/prediction.py` | Central prediction engine & calibration | Core API | **PRODUCTION** | Real | None | None | Probabilities sum to 1 | Enforce NO_TRADE implies actionable=False |
| `cryptoscope-ai/services/data_quality.py` | Multi-criteria data quality scoring service | Validation | **PRODUCTION** | Real | None | None | Replaces constants | Dynamically scores freshness and completeness |
| `cryptoscope-ai/services/backtest.py` | Realistic backtesting engine with slippage | Quant Research | **PRODUCTION** | Real | None | None | Zero fake stats | Computes true gross profit/loss and Sortino |
| `cryptoscope-ai/services/paper_trading.py` | Paper portfolio balance and trade engine | Paper Trading | **PRODUCTION** | Real | None | None | None | Manage user paper balances and execution |
| `cryptoscope-ai/apps/telegram/bot.py` | Telegram bot consuming canonical API | Telegram | **PRODUCTION** | Real | None | Bot token in env | None | Uses canonical `/api/v1` routes and real data |
| `legacy/backend/main.py` | Legacy v1 FastAPI implementation | Deprecated | **LEGACY** | Mixed | Duplicate of apps/api | Deprecated | Deprecated | Retained for historical audit with NON_PRODUCTION.md |
| `legacy/backend/NON_PRODUCTION.md` | Notice designating legacy backend as non-prod | Documentation | **DOC_ONLY** | Real | None | None | None | Prohibits deployment of legacy server |
