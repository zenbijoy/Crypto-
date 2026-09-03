# CryptoScope AI — System Architecture Specification

---

## 🏛️ High-Level System Architecture

```
Exchange WebSockets (Binance, Bybit, OKX)
    ↓
Validation & Normalization (Point-in-Time timestamping)
    ↓
Order Book Reconstruction & Trade-Flow Engine (CVD, Depth 5-50 bps, Microprice)
    ↓
Streaming Feature Engine & Online Feature Store
    ↓
Multi-Modal Expert Models (Tree, TCN, TFT, Microstructure CNN)
    ↓
Probability Calibration (Platt Scaling, Temperature Scaling)
    ↓
Multi-Expert Ensemble & Model Agreement Computation
    ↓
Market Regime Filter (HMM / GMM / Event Risk)
    ↓
Independent Deterministic Risk Engine & Circuit Breakers (ALLOW / REDUCE / REJECT)
    ↓
Signal Generator with Strict NO-TRADE Abstention
    ↓
Distribution Layer (FastAPI REST / WebSockets / Telegram Bot / Jetpack Compose Android Client)
```

---

## 🔒 Security & SRE Principles

- **Zero-Secret Hardcoding**: All exchange tokens, database credentials, and bot keys are managed exclusively via environment variables and secret stores.
- **Read-Only Analytics**: System requires zero withdrawal or trading execution credentials by default.
- **Circuit Breaker Triggers**: Automatic signal suspension upon feed staleness (>5s), excessive spread (>15 bps), or extreme model disagreement.
