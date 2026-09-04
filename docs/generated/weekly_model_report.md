# Weekly Model Performance & Challenger Evaluation Report

**Week Ending**: 2026-09-03  
**Audience**: Quant Research, MLOps, and Platform Risk Committee  

---

## 1. Champion vs. Challenger Matrix (BTCUSDT 15m)

| Role | Model Architecture | Sample Count | Brier Score | MCC | ECE | P95 Latency | Shadow Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Champion** | `TCN_DEEP_FORECASTER_V2` | 672 | 0.1982 | +0.1245 | 0.048 | 18.5 ms | **LIVE_SERVING** |
| **Challenger 1** | `PATCH_TST_CANDIDATE_V1` | 672 | 0.1965 | +0.1290 | 0.051 | 38.2 ms | **SHADOW_TRACKING** |
| **Challenger 2** | `LIGHTGBM_FAST_V2` | 672 | 0.2010 | +0.1180 | 0.042 | 4.8 ms | **SHADOW_TRACKING** |

### Evaluation Notes:
- **Challenger 1 (`PATCH_TST`)**: Marginally outperforms champion in Brier (-0.0017) and MCC (+0.0045), but exhibits 2.06x higher inference latency and 3.4x training memory footprint. Under Phase 37 Model Complexity Penalty guidelines, promotion to production is deferred pending further shadow observation.
- **Challenger 2 (`LIGHTGBM_FAST`)**: Demonstrates ultra-low latency (4.8 ms) and superior calibration (ECE 0.042) with competitive directional edge, serving as the certified fallback.

---

## 2. Regime-Stratified Performance Breakdown

| Market Regime | Observations | Accuracy (%) | Brier Score | Actionable Coverage (%) |
| :--- | :--- | :--- | :--- | :--- |
| **TRENDING_BULL** | 210 | 68.4% | 0.1820 | 48.2% |
| **TRENDING_BEAR** | 185 | 66.5% | 0.1895 | 44.0% |
| **LOW_VOL_CHOP** | 225 | 51.2% | 0.2310 | 12.4% (98.6% abstention) |
| **EXTREME_VOL_SPIKE** | 52 | 58.0% | 0.2180 | 19.2% (De-risked sizing) |

---

## 3. Drift & Calibration Diagnostics

- **Feature Importance Stability**: Zero significant SHAP drift detected over the 7-day window. Microstructure factors (`order_imbalance`, `spread_bps`, `cvd_quote`) maintain 68.4% aggregate attribution weight.
- **Mixture of Experts**: Gated weights remain balanced with no single-expert collapse (Max individual expert weight: 44.2%).
- **Out-of-Distribution Rejection**: The OOD Mahalanobis detector rejected 8 transient price spike events during venue liquidation cascades, avoiding false entries.
