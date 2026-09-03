# CryptoScope AI — Enterprise Crypto Futures Intelligence & Microstructure Forecasting Platform

---

## 🎯 Master Overview

**CryptoScope AI** is a quantitative crypto-market forecasting and intelligence platform targeting perpetual futures on **Bitcoin (BTC)**, **Ethereum (ETH)**, and **Solana (SOL)**.

The system synthesizes spot markets, perpetual futures positioning, high-frequency order books, trade flow delta, liquidation activity, on-chain metrics, macroeconomic variables, news sentiment, and cross-asset lead-lag relationships into **uncertainty-aware probabilistic forecasts**.

> ⚠️ **Core Philosophy:** The product does **NOT** claim guaranteed profitability or guaranteed 99% accuracy. Instead, it optimizes for **calibrated probabilities**, **positive expected edge after transaction costs/slippage**, **explainable predictions via SHAP**, and **automatic abstention through NO-TRADE states**.

---

## 📐 Key Capabilities

1. **Multi-Horizon Probabilistic Forecasting**:
   - Timeframes: 1m, 5m, 15m, 30m, 1h, 4h, 12h, 1d.
   - Direction probabilities: $P(\text{UP}), P(\text{DOWN}), P(\text{SIDEWAYS})$.
   - Widening Quantile Fan-Chart: $P_{10}, P_{25}, P_{50}, P_{75}, P_{90}$.
2. **Order Book Microstructure Engine**:
   - L2 Order Book Depth within 5, 10, 25, 50 bps.
   - Microprice $P_{\text{micro}} = \frac{P_a V_b + P_b V_a}{V_a + V_b}$.
   - Multi-level Order Book Imbalance (OBI), Book Convexity, and Liquidity Wall persistence tracking.
3. **Trade-Flow & CVD Engine**:
   - Signed trade imbalance, Cumulative Volume Delta (CVD), and rolling percentile whale transaction detection.
4. **Derivatives & Liquidation Intelligence**:
   - 7-day Funding Rate z-score, Open Interest velocity, and Market State Inference ($P \uparrow + \text{OI} \uparrow \implies \text{New Long Expansion}$).
   - Liquidation Heatmap clusters and `LIQUIDATION_PRESSURE_SCORE` ($0–100$).
5. **Deterministic Risk Engine & Circuit Breakers**:
   - Independent risk veto (`ALLOW`, `REDUCE`, `REJECT`).
   - Circuit breakers for stale feeds, WebSocket desync, latency spikes, and abnormal spread.
6. **Strict Anti-Leakage Framework**:
   - Chronological walk-forward validation with embargo periods.
   - Point-in-time data integrity ($T_{\text{available}} \le T_{\text{prediction}}$).
7. **Production Telegram Intelligence Bot**:
   - Full command suite (`/predict`, `/chart`, `/levels`, `/funding`, `/oi`, `/liquidations`, `/regime`, `/performance`).
   - Standardized prediction report with structured feature drivers and regulatory disclaimers.

---

## 🚀 Getting Started

### Local Development
```bash
# 1. Clone and enter directory
cd cryptoscope-ai

# 2. Setup environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Launch FastAPI Server
uvicorn apps.api.main:app --host 0.0.0.0 --port 8000 --reload
```

Interactive OpenAPI Documentation: 👉 **http://localhost:8000/docs**

### Run Leakage & Unit Tests
```bash
pytest tests/ -v
```

---

## 📜 Regulatory Disclaimer
> *"Probabilistic market analysis — not a guarantee of future performance."*
