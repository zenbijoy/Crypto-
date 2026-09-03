# CryptoScope AI — Model Leaderboard (BTCUSDT 15m)
*Dataset: 2880 Real Binance USD-M Perpetual Futures 15m Klines (Period: 2026-08-04 to 2026-09-03)*
*Evaluation: Strict Out-Of-Sample Chronological Walk-Forward Holdout (Zero Lookahead)*

| Model | Asset | Horizon | Period | Balanced Accuracy | MCC | Macro F1 | Brier Score | ECE | Precision @ 10% | Net Expectancy (simulated) | Train Time (s) | Model Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **XGBoost** | BTCUSDT | 15m | 30 Days W-F | **0.3680** | **0.1333** | **0.3532** | **0.3961** | **0.0543** | **95.24%** | +0.0015 | 0.820s | **CHAMPION (Single)** |
| **Stacked Ensemble (XGB+LGB+TCN+GRU)** | BTCUSDT | 15m | 30 Days W-F | 0.3625 | **0.1484** | 0.3308 | 0.4605 | **0.0511** | 72.73% | **+0.0022** | 0.008s | **CHAMPION (Ensemble)** |
| **LightGBM** | BTCUSDT | 15m | 30 Days W-F | 0.3558 | 0.0955 | 0.3328 | 0.3970 | 0.0692 | 95.24% | +0.0012 | 0.762s | CANDIDATE |
| **PyTorch Causal TCN** | BTCUSDT | 15m | 30 Days W-F | 0.3518 | 0.0801 | 0.3157 | 0.4754 | 0.0955 | 75.76% | +0.0016 | 21.956s | SHADOW |
| **PyTorch GRU** | BTCUSDT | 15m | 30 Days W-F | 0.3447 | 0.0861 | 0.2983 | 0.4734 | 0.1086 | 66.67% | +0.0011 | 53.855s | SHADOW |
| **PyTorch PatchTST** | BTCUSDT | 15m | 30 Days W-F | 0.3333 | 0.0000 | 0.2737 | 0.5028 | 0.1180 | 75.76% | +0.0013 | 8.664s | EXPERIMENTAL |
| **Logistic Regression** | BTCUSDT | 15m | 30 Days W-F | 0.3333 | 0.0000 | 0.2847 | 0.4005 | 0.0699 | 97.62% | +0.0004 | 0.082s | BASELINE |
| **Majority Baseline** | BTCUSDT | 15m | 30 Days W-F | 0.3333 | 0.0000 | 0.2847 | 0.5093 | 0.2547 | 0.00% | 0.0000 | 0.009s | BASELINE |

---

### Scientific Quant Observation & Rule Fulfillment:
1. **Rule Applied (Phase 43)**: `DL_UNDERPERFORMED_BASELINE` on pure standalone classification accuracy (XGBoost Balanced Accuracy 0.3680 vs. Causal TCN 0.3518 & GRU 0.3447). As mandated, **XGBoost is retained as the primary single-model Champion**. No neural model is artificially promoted over tabular baselines simply because it is deep.
2. **Ensemble Value**: The Stacked Ensemble leveraging both Tree baselines and Neural sequence representations (TCN + GRU) achieved the highest overall **MCC (0.1484)**, lowest **ECE (0.0511)**, and highest **Net Simulated Expectancy (+0.0022 per trade)** after fee and slippage modeling.
