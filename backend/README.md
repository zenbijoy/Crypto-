# CryptoScope AI — Python FastAPI Backend

Enterprise Crypto Futures Intelligence & Microstructure Forecasting API.

---

## ⚡ Features

- **Asynchronous FastAPI Engine**: Non-blocking RESTful endpoints for real-time tickers, candlesticks, order book depth, liquidations, on-chain metrics, macro calendars, and machine learning inferences.
- **Authentication & Security**: JWT Bearer token authentication (`/v1/auth/login`, `/v1/auth/profile`), secure hashing, and role-based permissions.
- **Probabilistic Forecasting (`/v1/predictions/{symbol}`)**: Fan-chart quantiles ($P_{10}, P_{25}, P_{50}, P_{75}, P_{90}$), model agreement metrics, and strict **"no-trade" discipline** gating.
- **Market Microstructure & Derivatives**: 
  - Order book imbalance ($I = \frac{V_b - V_a}{V_b + V_a}$) and depth within 10–25 bps.
  - Liquidation heatmaps and high-leverage magnetic cluster detection.
  - Multi-exchange funding rates (Binance, Bybit, OKX) and open interest expansion.
- **Real-Time WebSockets (`/ws`)**: High-frequency streaming price feeds, order flow imbalance ticks, and probability distributions.
- **Risk-Gated Paper Trading (`/v1/paper/*`)**: Realistic slippage, fee simulation (0.04% taker / 0.02% maker), margin monitoring, and position risk telemetry.

---

## 🚀 Quickstart

### 1. Install Dependencies
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run the Server
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Interactive OpenAPI Swagger documentation will be available at:
👉 **http://localhost:8000/docs**

---

## 📡 API Endpoints Overview

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/v1/auth/login` | Authenticate user and receive JWT access token |
| `GET` | `/v1/auth/profile` | Retrieve user profile, active alerts, and sync status |
| `GET` | `/v1/markets` | Live snapshot of all tracked futures pairs |
| `GET` | `/v1/markets/{symbol}` | Detail metrics for specific symbol (e.g. `BTCUSDT`) |
| `GET` | `/v1/candles/{symbol}` | OHLCV candlestick data (15m, 1h, 4h, 1d) |
| `GET` | `/v1/predictions/{symbol}` | Probabilistic AI forecast, fan chart quantiles & feature attributions |
| `GET` | `/v1/orderbook/{symbol}` | L2 order book depth, spread bps, microprice, and imbalance |
| `GET` | `/v1/derivatives/{symbol}` | Open interest, funding rate 7d z-score, long/short ratio |
| `GET` | `/v1/liquidations/{symbol}` | Liquidation pressure score, magnetic clusters & recent cascades |
| `GET` | `/v1/levels/{symbol}` | Support/resistance zones, volume POC, and structural trend |
| `GET` | `/v1/sentiment/{symbol}` | Fear & Greed index, curated crypto news sentiment |
| `GET` | `/v1/onchain/{asset}` | Exchange netflow, whale deposits, SOPR, and MVRV |
| `GET` | `/v1/macro` | High-impact economic calendar, DXY, US 10Y, and VIX |
| `GET` | `/v1/alerts` | Get user-configured quantitative alert rules |
| `POST` | `/v1/alerts` | Create new multi-condition AI alert rule |
| `DELETE` | `/v1/alerts/{id}` | Delete alert rule |
| `GET` | `/v1/paper/positions` | List open paper trading positions |
| `POST` | `/v1/paper/order` | Place simulated order with realistic slippage |
| `POST` | `/v1/paper/positions/{id}/close` | Market close open simulated position |
| `GET` | `/v1/performance` | Track historical ML model precision, Brier score, and coverage |
| `GET` | `/v1/models` | Champion vs Challenger model registry and drift monitoring |
| `GET` | `/v1/system/health` | Real-time latency, provider sync, and circuit breaker status |
| `WS` | `/ws` | Streaming WebSocket for real-time market ticks & book pressure |
