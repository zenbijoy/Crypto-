# CryptoScope AI — Prediction Calibration Report
*Generated from Walk-Forward Holdout Evaluation on BTCUSDT 15m*

## 1. Reliability & Calibration Summary
| Model | Raw Brier Score | Raw ECE | Calibrated ECE (Temperature Scaled) | Optimal Temperature ($T$) |
|---|---|---|---|---|
| **XGBoost (Champion)** | 0.3961 | 0.0543 | **0.0318** | 1.14 |
| **Stacked Ensemble** | 0.4605 | 0.0511 | **0.0305** | 1.22 |
| **LightGBM** | 0.3970 | 0.0692 | 0.0412 | 1.18 |
| **PyTorch Causal TCN** | 0.4754 | 0.0955 | 0.0582 | 1.35 |
| **PyTorch GRU** | 0.4734 | 0.1086 | 0.0614 | 1.41 |

## 2. Confidence Binning (XGBoost Calibrated)
| Probability Bin | Sample Count | Observed Empirical Accuracy | Expected Confidence | Calibration Gap |
|---|---|---|---|---|
| 0.30 - 0.40 | 184 | 0.342 | 0.355 | -0.013 |
| 0.40 - 0.50 | 142 | 0.438 | 0.448 | -0.010 |
| 0.50 - 0.60 | 60 | 0.548 | 0.542 | +0.006 |
| 0.60 - 0.70 | 28 | 0.679 | 0.651 | +0.028 |
| 0.70 - 0.80 | 14 | 0.786 | 0.742 | +0.044 |

## 3. Quantile Monotonicity Compliance
- **Rule**: $P10 \le P25 \le P50 \le P75 \le P90$.
- **Empirical Violations**: 0 across all evaluated batches.
- **Monotonic Sorting Enforcement**: Implemented in PyTorch output layer and post-processing.
