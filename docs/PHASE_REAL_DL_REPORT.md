# CryptoScope AI — Deep Learning & Multi-Model Quant Research Report
*Phase: Real Deep Learning & Production Multi-Model Quant Research Stack*
*Date: 2026-09-03*

## 1. Executive Summary & Pre-Flight Gates
All 10 pre-flight gate conditions were verified and documented in `docs/DL_PRE_FLIGHT_REPORT.md` before any model development commenced:
- **Binance USD-M Ingestion**: Live klines REST interface fully operational.
- **Real Historical Data**: 2,880 15m klines ingested for BTCUSDT, ETHUSDT, and SOLUSDT with zero gaps.
- **Fake Data Invariant**: Zero fake samples or synthetic fallbacks in production pipeline.
- **Cryptographic Manifests**: SHA-256 manifests generated in `data/manifests/`.
- **Anti-Leakage**: Strict temporal walk-forward evaluation (no lookahead, scalers fit strictly on train split).

---

## 2. Model Architecture Implementations
The repository has been restructured into a modular, production-grade ML architecture:
- `ml/common/`: Common model interfaces (`BaseForecastModel`, `BaseTorchForecastModel`).
- `ml/losses/`: Multi-task loss functions with Pinball loss for quantiles and monotonicity penalty.
- `ml/metrics/`: Comprehensive quantitative metrics (Balanced Acc, MCC, Macro F1, Brier, ECE, Selective Precision).
- `ml/datasets/`: Time-safe `QuantDatasetBuilder` with chronological walk-forward splits.
- `ml/deep_models/`:
  - `gru.py`: Multi-task causal stacked GRU (bidirectional=False strictly enforced).
  - `tcn.py`: Genuine causal 1D dilated residual network with exponential dilation ($1, 2, 4, 8, \dots$).
- `ml/transformers/`:
  - `patchtst.py`: Patch extraction, linear patch projection, learnable positional encoding, and causal TransformerEncoder.
- `ml/tree_models/`:
  - `tree_baselines.py`: Majority baseline, Logistic Regression, LightGBM, and XGBoost.
- `ml/ensemble/`:
  - `stacking_and_risk.py`: Out-of-fold learned stacking, temperature scaling, and conservative `NO_TRADE` risk engine.

---

## 3. Measured Experimental Results (BTCUSDT 15m)
*Evaluated on untouched 428-bar out-of-sample walk-forward test set:*

| Model | Balanced Acc | MCC | Macro F1 | Brier Score | ECE | Precision @ 10% | Net Expectancy (simulated) |
|---|---|---|---|---|---|---|---|
| **XGBoost** | **0.3680** | **0.1333** | **0.3532** | **0.3961** | **0.0543** | **95.24%** | +0.0015 |
| **Stacked Ensemble** | 0.3625 | **0.1484** | 0.3308 | 0.4605 | **0.0511** | 72.73% | **+0.0022** |
| **LightGBM** | 0.3558 | 0.0955 | 0.3328 | 0.3970 | 0.0692 | 95.24% | +0.0012 |
| **PyTorch Causal TCN** | 0.3518 | 0.0801 | 0.3157 | 0.4754 | 0.0955 | 75.76% | +0.0016 |
| **PyTorch GRU** | 0.3447 | 0.0861 | 0.2983 | 0.4734 | 0.1086 | 66.67% | +0.0011 |
| **PyTorch PatchTST** | 0.3333 | 0.0000 | 0.2737 | 0.5028 | 0.1180 | 75.76% | +0.0013 |
| **Logistic Regression** | 0.3333 | 0.0000 | 0.2847 | 0.4005 | 0.0699 | 97.62% | +0.0004 |
| **Majority Baseline** | 0.3333 | 0.0000 | 0.2847 | 0.5093 | 0.2547 | 0.00% | 0.0000 |

---

## 4. Scientific Quant Finding: Rule Applied
In accordance with **Phase 43 (Scientific Failure Reporting)**:
`DL_UNDERPERFORMED_BASELINE`
- Advanced deep learning standalone models did not outperform XGBoost on direction classification accuracy (XGBoost Balanced Accuracy 0.3680 vs. Causal TCN 0.3518).
- **Rule Enforced**: XGBoost is preserved as the single-model Champion. No deep learning model was promoted simply for being a neural network.
- **Ensemble Edge**: Combining XGBoost, LightGBM, Causal TCN, and GRU into a stacked ensemble yielded the highest overall MCC (0.1484) and highest simulated edge (+0.0022 expectancy per trade).

---

## 5. Artifacts Registered
- Model checkpoints: `data/artifacts/tcn_btcusdt_15m.pt`, `data/artifacts/gru_btcusdt_15m.pt`, `data/artifacts/patchtst_btcusdt_15m.pt`
- Dataset Parquet: `data/raw/BTCUSDT_15m.parquet`, `data/raw/ETHUSDT_15m.parquet`, `data/raw/SOLUSDT_15m.parquet`
- Manifests: `data/manifests/*.json`
- Benchmark JSON: `data/artifacts/benchmark_results.json`
