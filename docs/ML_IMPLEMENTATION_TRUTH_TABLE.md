# CryptoScope AI — Machine Learning Implementation Truth Table

**Purpose**: Forensic verification and transparency disclosure for all statistical, heuristic, and machine learning components across the repository.  
**Auditor**: Principal Machine Learning & Quantitative Systems Engineer  
**Policy**: Zero false architectural claims. Explicit labeling of baseline heuristics vs genuine trained neural/tree artifacts.  

---

## 1. Complete Model Inventory & Truth Matrix

| File Path | Claimed Model Family | Actual Implementation | Trainable? | Artifact Required? | External Dependencies | Real Training Implemented? | Out-of-Sample Validation? | Production Eligible Status |
|---|---|---|---|---|---|---|---|---|
| `ml/models/tabular_expert.py` | XGBoost Gradient Boosted Trees | `HeuristicTabularBaseline` (RSI, MACD, 24h realized volatility, skewness scoring) | No | No (Parametric heuristic) | Python Standard (`math`) | No (Explicit quantitative rule-based baseline) | N/A (Analytical baseline) | **ELIGIBLE AS HEURISTIC BASELINE** (Truthfully labeled `EXPERIMENTAL_HEURISTIC`) |
| `ml/models/orderflow_tcn.py` | Temporal Convolutional Network (TCN) | `HeuristicOrderflowBaseline` (Orderbook Imbalance 10bps, Microprice drift, Spread factor) | No | No (Parametric heuristic) | Python Standard (`math`) | No (Explicit microstructure rule-based baseline) | N/A (Analytical baseline) | **ELIGIBLE AS HEURISTIC BASELINE** (Truthfully labeled `EXPERIMENTAL_HEURISTIC`) |
| `ml/models/temporal_tft.py` | Temporal Fusion Transformer (TFT) | `HeuristicTemporalBaseline` (Relative strength vs BTC, Volatility step sigma, Quantiles P10-P90) | No | No (Parametric heuristic) | Python Standard (`math`) | No (Explicit multi-horizon rule-based baseline) | N/A (Analytical baseline) | **ELIGIBLE AS HEURISTIC BASELINE** (Truthfully labeled `EXPERIMENTAL_HEURISTIC`) |
| `ml/models/derivatives_expert.py` | Derivatives Intelligence Model | Quant heuristic on Funding Rate Z-score, Basis bps, and Open Interest velocity | No | No (Parametric heuristic) | Python Standard (`math`) | No | N/A | **ELIGIBLE AS HEURISTIC BASELINE** |
| `ml/models/context_expert.py` | Regime & Macro Sentiment Model | Sentiment index, BTC dominance, and Macro regime weighted scoring | No | No (Parametric heuristic) | Python Standard | No | N/A | **ELIGIBLE AS HEURISTIC BASELINE** |
| `ml/deep_models/tcn.py` | Causal Dilated Residual TCN | PyTorch `nn.Module` causal dilated Conv1d with weight normalization and residual connections | Yes | Yes (`.pt` / `.pth` state dict) | `torch` | Yes (Architecture fully coded in `tcn.py`) | Purged K-fold with embargo | **RESEARCH / CANDIDATE** (Requires trained `.pt` artifact in registry) |
| `ml/deep_models/gru.py` | Bidirectional Recurrent Sequence | PyTorch `nn.Module` multi-layer bidirectional GRU with linear classification head | Yes | Yes (`.pt` state dict) | `torch` | Yes (Architecture fully coded in `gru.py`) | Chronological walk-forward | **RESEARCH / CANDIDATE** (Requires trained `.pt` artifact in registry) |
| `ml/transformers/patchtst.py` | Patch Time-Series Transformer | PyTorch `nn.Module` sub-series patch projection, multi-head self-attention, and flattening head | Yes | Yes (`.pt` state dict) | `torch` | Yes (Architecture fully coded in `patchtst.py`) | Purged rolling holdout | **RESEARCH / CANDIDATE** (Requires trained `.pt` artifact in registry) |
| `ml/tree_models/tree_baselines.py` | GBDT Baselines (LightGBM/XGBoost) | Python wrapper class for training and evaluating scikit-learn / LightGBM regressors | Yes | Yes (`.booster` / `.joblib`) | `scikit-learn`, `lightgbm` (optional) | Yes (Code scaffolding present) | Out-of-bag validation | **RESEARCH / CANDIDATE** (Requires artifact) |
| `ml/experts/learned_moe.py` | Learned Mixture of Experts | Softmax gating network over tabular, orderflow, and temporal experts conditioned on regime | Yes | Optional (Trained gating weights or analytical priors) | Python Standard / PyTorch | Yes | Cross-regime stability check | **PRODUCTION** (Active ensemble coordinator) |
| `services/prediction.py` | Canonical Prediction Engine | Enforces probability simplex ($\sum p_i = 1.0$), calibration, epistemic/aleatoric uncertainty, NO_TRADE filter | Engine | No (Orchestrator) | Python Standard | N/A | Point-in-time test assertions | **PRODUCTION** (Canonical engine) |

---

## 2. Architectural Integrity Declarations

1. **Explicit Naming Truth**: Every heuristic model class is named `Heuristic*Baseline` and exports metadata with `is_trained_deep_learning = False` and `is_heuristic_baseline = True`.
2. **Registry Stage Safety**: Any newly registered model defaults to `EXPERIMENTAL`. A model may only achieve `PRODUCTION` stage if an inspected, checksum-verified artifact and schema match exist.
3. **Graceful Degradation**: When a deep learning neural artifact (`.pt`) is absent, the system does not invent synthetic neural weights; it falls back to the transparent, calibrated `Heuristic*Baseline` models and documents this in the response metadata.
