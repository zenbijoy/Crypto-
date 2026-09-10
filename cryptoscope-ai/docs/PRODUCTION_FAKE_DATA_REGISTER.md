# CryptoScope AI — Production Fake Data Register

**Purpose**: Systematic forensic register of all synthetic, simulated, mock, or hardcoded financial observations across the repository, tracking their eradication, real replacements, and current status.  
**Strict Policy**: ZERO unresolved fake market observations, zero constant data-quality scores, zero synthetic forecast probabilities in production code paths.  
**Auditor**: Principal Forensic Quant Architect  

---

## 1. Production Fake Data Scan & Rectification Register

| ID | File | Line / Function | Meaning / Finding | Consumer | Severity | Replacement / Resolution | Status |
|---|---|---|---|---|---|---|---|
| **FD-01** | `providers/exchanges/binance.py` | `BinanceAdapter.fetch_ticker` | Legacy hardcoded prices: `BTC=67500.0, ETH=3500.0, SOL=145.0, DOGE=0.125` | Ingestion / Registry | **P0** | Replaced with real Binance USD-M public REST `https://fapi.binance.com/fapi/v1/ticker/24hr` | **RESOLVED** |
| **FD-02** | `providers/exchanges/binance.py` | `BinanceAdapter.fetch_ohlcv` | Synthetic candle generation around `base_p` | Market Data API | **P0** | Replaced with real Binance `/fapi/v1/klines` multi-timeframe OHLCV | **RESOLVED** |
| **FD-03** | `providers/exchanges/binance.py` | `BinanceAdapter.fetch_trades` | Generated trades with static `$67,500.0` price | Market Data API | **P0** | Replaced with real Binance `/fapi/v1/trades` live execution tape | **RESOLVED** |
| **FD-04** | `providers/exchanges/binance.py` | `BinanceAdapter.fetch_orderbook` | Algorithmic ladder based on `base_p` | Orderbook API | **P0** | Replaced with real Binance `/fapi/v1/depth` L2 snapshot | **RESOLVED** |
| **FD-05** | `providers/exchanges/binance.py` | `BinanceAdapter.fetch_derivatives_snapshot` | Hardcoded `funding_rate=0.000100`, static OI | Derivatives API | **P0** | Replaced with real Binance `/fapi/v1/premiumIndex` & `/openInterest` | **RESOLVED** |
| **FD-06** | `apps/api/main.py` | `canonical_envelope` | Defaulted sources to `["BINANCE", "BYBIT", "OKX", "COINBASE", "HYPERLIQUID"]` regardless of usage | API Clients / DTOs | **P1** | Replaced with dynamic source provenance reflecting only verified responding providers | **RESOLVED** |
| **FD-07** | `apps/api/main.py` | CORS Configuration | Wildcard `allow_origins=["*"]` combined with `allow_credentials=True` | Security / Browser | **P0** | Replaced with explicit `settings.CORS_ORIGINS` from centralized configuration | **RESOLVED** |
| **FD-08** | `ml/models/tabular_expert.py` | `HeuristicTabularBaseline` | Claimed model type XGBoost in legacy headers | Prediction Engine | **P1** | Labeled explicitly as `EXPERIMENTAL_HEURISTIC` baseline with `is_trained_deep_learning=False` | **RESOLVED** |
| **FD-09** | `ml/models/orderflow_tcn.py` | `HeuristicOrderflowBaseline` | Claimed model type TCN in legacy headers | Prediction Engine | **P1** | Labeled explicitly as `EXPERIMENTAL_HEURISTIC` baseline with `is_trained_deep_learning=False` | **RESOLVED** |
| **FD-10** | `ml/models/temporal_tft.py` | `HeuristicTemporalBaseline` | Claimed model type TFT in legacy headers | Prediction Engine | **P1** | Labeled explicitly as `EXPERIMENTAL_HEURISTIC` baseline with `is_trained_deep_learning=False` | **RESOLVED** |
| **FD-11** | `services/data_quality.py` | Quality Scoring | Static `data_quality_score = 98` | Quality Gate | **P1** | Replaced with dynamic `DataQualityService` evaluating freshness, completeness, and skew | **RESOLVED** |
| **FD-12** | `services/prediction.py` | Prediction Invariants | Non-normalized probabilities or actionable NO_TRADE | Client Signals | **P0** | Enforced $\sum p_i = 1.0$ and `NO_TRADE` $\implies$ `actionable = False` | **RESOLVED** |
| **FD-13** | `services/backtest.py` | Performance Metrics | Hardcoded `profit_factor = 2.45`, arbitrary Sortino | Research Engine | **P1** | Replaced with real gross profit/loss ratio and true downside deviation calculations | **RESOLVED** |
| **FD-14** | `legacy/backend/` (former `backend/main.py` and `api/*`) | Entire Server | Competing backend server with duplicate endpoints and hardcoded prediction stubs | Deployment | **P0** | Quarantined to `legacy/backend/` with `NON_PRODUCTION.md`, top-level `api/` removed, and `AIAnalysisService.get_prediction` gated/deprecated | **RESOLVED** |
| **FD-15** | `app/src/main/java` | `CryptoViewModel.kt` | UI state defaulting to realistic mock prices | Android Presentation | **P1** | Cleaned initial state to `UiState.Loading` / `Live Flow` waiting for real backend/exchange data | **RESOLVED** |

---

## 2. Verification Invariant Summary

- **Total Production Fake Observations Identified**: 15
- **Total Resolved**: 15 (100%)
- **Total Unresolved in Production**: 0
- **Automated Guard**: Continuous static analysis and unit test assertion (`test_zero_synthetic_data_in_production`).
