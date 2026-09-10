# Fake-Data Register

This register documents all identified instances of fabricated financial data, synthetic fallback numbers, hardcoded market metrics, and simulated provider states across the codebase.

## Forensic Findings & Action Plan

| File | Line/Function | Fake Value | What It Represents | Production Impact | Replacement Strategy | Fixed Status |
|---|---|---|---|---|---|---|
| `backend/main.py` & `api/` | Full files | `random.uniform`, synthetic candles, mock ticks, hardcoded fake predictions | Monolithic duplicate backend with simulated market data and hardcoded prediction stubs | High: Misleads clients with synthetic prices and predictions | Deprecate and isolate under legacy/backend/; use cryptoscope-ai exclusively | **DEPRECATED & ISOLATED IN legacy/backend/** |
| `cryptoscope-ai/services/feature_engine.py` | Line 44 (`compute_all_features`) | `default_prices = {"BTC": 67500.0, ...}` | Fabricated candle closes when history is empty | High: ML models receive fabricated inputs | Return `DataUnavailableException` or `FeatureUnavailable` when candles < 2 | **FIXED / ZERO FAKE DATA** |
| `cryptoscope-ai/services/feature_engine.py` | Line 230 | `meme_sector_factor: 14.5%` | Fabricated social volume and retail flow for meme tokens | Medium: Injects fake altcoin data | Return `None` or real on-chain/social provider data if configured | **FIXED / ZERO FAKE DATA** |
| `cryptoscope-ai/services/prediction.py` | Line 57 (`generate_forecast`) | `defaults = {"BTC": 67500.0, ...}` | Fabricated price fallback when current_price is None | High: Generates fake forecast when market is disconnected | Refuse fabrication: enforce `DataUnavailableException` or Truthful Abstention | **FIXED / ZERO FAKE DATA** |
| `cryptoscope-ai/ml/models/meta_ensemble.py` | Line 74 (`predict_ensemble`) | `price_feats.get("close", 67500.0)` | Hardcoded BTC price fallback | High: Corrupts expected dollar quantile bounds | Mark ensemble prediction unavailable if close price is missing | **FIXED / ZERO FAKE DATA** |
| `cryptoscope-ai/services/aggregation.py` | Line 74 (`aggregate_ticker`) | `[67500.0 if asset.upper() == "BTC" ...]` | Hardcoded price fallback in ticker aggregation | High: Emits consensus price when zero venues responded | Return `None` and flag venue_count = 0 | **FIXED / ZERO FAKE DATA** |
| `cryptoscope-ai/services/backtest.py` | Lines 73-74 (`run_backtest`) | `"profit_factor": 1.78`, `"coverage_pct": 28.5` | Hardcoded backtest performance metrics | High: Falsely reports algorithmic profitability | Compute dynamically from actual trades executed, fee models, and slippage | **FIXED / ZERO FAKE DATA** |
| `cryptoscope-ai/providers/enrichment.py` | `get_macro_context`, `get_defi_metrics` | Hardcoded DXY (104.2), 10Y Yield (4.28%), TVL ($88B) | Mock macroeconomic and DeFi telemetry | Medium: Fabricates macro market conditions | Return `DATA_UNAVAILABLE` or `NOT_CONFIGURED` unless FRED / DefiLlama API key configured | **FIXED / ZERO FAKE DATA** |
| `app/src/main/java/com/example/core/data/CryptoScopeRepository.kt` | `_marketDetails`, `_optionsData` | Hardcoded CVD, options gamma, funding rates | Local simulation of derivatives and options analytics | High: Android app displays fake analytics | Point Android directly to live Binance Futures REST/WS and canonical endpoints | **FIXED / ZERO FAKE DATA** |
| `app/src/main/java/com/example/core/data/CryptoScopeRepository.kt` | `_providerHealth` | Fixed `"CONNECTED"`, latency 24ms | Hardcoded exchange provider statuses | Medium: Masks network drops or venue degradation | Read actual health from live socket state and provider readiness registry | **FIXED / ZERO FAKE DATA** |

## Goal:
At the conclusion of these phases, all items above must be resolved to **FIXED / ZERO FAKE DATA**.
