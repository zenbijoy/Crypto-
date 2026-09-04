# CryptoScope AI — MLflow MLOps Architecture

**Experiment Tracking, Model Registry, Governance & Model Serving**  

---

## 1. MLOps Lifecycle & Registry Stages

Every machine learning model (GBDT, TCN, PatchTST) follows a formal promotion pipeline managed via MLflow:

```
[ Raw Quant Data ]
        │
        ▼
[ Feature Engineering (Anti-Leakage Validated) ]
        │
        ▼
[ Chronological Walk-Forward Training & Calibration ]
        │
        ▼
[ MLflow Run Logging (Parameters, Artifacts, Brier Score, ECE, Sortino) ]
        │
        ▼
┌─────────────────────────────────────────────────────────────┐
│                   MLFLOW MODEL REGISTRY                     │
│                                                             │
│  Stage 1: EXPERIMENTAL   ──> Registered upon initial train  │
│  Stage 2: CANDIDATE      ──> Passes out-of-sample barriers  │
│  Stage 3: SHADOW         ──> Live inference parallel check  │
│  Stage 4: PAPER          ──> Evaluated in paper execution   │
│  Stage 5: PRODUCTION     ──> Active ensemble member         │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Model Artifact Manifest Requirements

Every model artifact registered in MLflow must bundle:
1. **Model Binary**: PyTorch `.pt` state dict or LightGBM `.booster` file.
2. **Feature Schema Definition**: Exact feature ordering, types, and imputation constants.
3. **Scaler & Transform Objects**: Fitted `RobustScaler` / `StandardScaler` fitted strictly on train-set.
4. **Probability Calibrator**: Isotonic regression or Platt scaling calibration model.
5. **Hyperparameter Manifest**: Learning rate, context length, patch size, dropout, weight decay.
6. **Provenance Metadata**: Git commit SHA, dataset hash, training date boundaries, backtest metrics.

---

## 3. Serving & Fallback Policy

- **No Synthetic Fallback**: If an active production model artifact is missing or corrupt, the serving engine emits `MODEL_UNAVAILABLE` rather than generating synthetic random numbers.
- **Parametric Baseline Graceful Degradation**: Where deep neural weights are not present, the system serves the explicitly labeled, mathematically calibrated `Heuristic*Baseline` models (`HeuristicTabularBaseline`, `HeuristicOrderflowBaseline`, `HeuristicTemporalBaseline`) with full transparency.
