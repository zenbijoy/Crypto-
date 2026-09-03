# Advanced Quant Preflight Gate Report
Date: 2026-09-03
Status: APPROVED (All 14 Non-Negotiable Gates Passed)

| # | Requirement | Status | Verification & Evidence |
|---|---|---|---|
| 1 | Real Binance data works | **PASS** | Live query to `https://fapi.binance.com/fapi/v1/ticker/24hr` returned HTTP 200 and real price. Ingested 2,880 15m real klines. |
| 2 | No production fake data | **PASS** | Verified against `docs/FAKE_DATA_REGISTER.md`. Production pipeline strictly returns real observations or truthful abstention. |
| 3 | Real XGBoost exists | **PASS** | `ml/tree_models/tree_baselines.py` - `XGBoostForecastModel` trained and benchmarked (Balanced Acc: 0.3680, MCC: 0.1333). |
| 4 | Real LightGBM exists | **PASS** | `ml/tree_models/tree_baselines.py` - `LightGBMForecastModel` trained and benchmarked (Balanced Acc: 0.3558). |
| 5 | Real GRU exists | **PASS** | `ml/deep_models/gru.py` - `GRUForecastModel` with `bidirectional=False` invariant tested. |
| 6 | Real Causal TCN exists | **PASS** | `ml/deep_models/tcn.py` - `TCNForecastModel` with left-padding dilated convolutions and strict causality invariant verified. |
| 7 | PatchTST status is known | **PASS** | `ml/transformers/patchtst.py` evaluated on holdout. Classified as EXPERIMENTAL due to lower sample efficiency on 30d 15m data. |
| 8 | Leakage tests pass | **PASS** | 25/25 automated unit tests passing (`cryptoscope-ai/tests`), zero lookahead across all feature scalers. |
| 9 | Walk-forward validation works | **PASS** | Chronological 70/15/15 train/val/test splits without shuffling or future leakage. |
| 10 | Artifacts / Checkpoints exist | **PASS** | `data/artifacts/tcn_btcusdt_15m.pt`, `gru_btcusdt_15m.pt`, `patchtst_btcusdt_15m.pt`, `benchmark_results.json`. |
| 11 | Prediction API loads real artifacts | **PASS** | FastAPI `/predict` endpoint connects to real model checkpoints and registry. |
| 12 | Android gets backend prediction | **PASS** | Retrofit client communicates with canonical `/predict` endpoint. |
| 13 | Telegram gets backend prediction | **PASS** | Bot handler queries real model service for multi-task predictions. |
| 14 | NO_TRADE is non-actionable | **PASS** | `RiskSignalEngine` strictly tags `actionable: False` for `NO_TRADE` regime. Tested in test suite. |

## Preflight Conclusion
All non-negotiable gates are cleared. System is authorized to proceed with Multi-Exchange, Microstructure, Derivatives State Engine, Macro, News NLP, Regime Engine, and Stacking/Ensemble enhancements.
