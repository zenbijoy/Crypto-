# CryptoScope AI — UI / Backend Contract Completion Matrix

**Classification**: Comprehensive Screen-by-Screen Field & Endpoint Audit  
**Auditor**: Senior Android / Kotlin Engineer & QA Architect  
**Principle**: Every visible UI element must trace to a real backend endpoint, verified exchange provider, or deterministic client calculation. Zero fake initial states.  

---

## 1. Screen-by-Screen Field Mapping & Telemetry Audit

| Screen Name | Visible UI Element / Field | Backend API Endpoint | Provider / Calculation Engine | Freshness SLA | Data Classification | Completion Status |
|---|---|---|---|---|---|---|
| **HomeScreen** | Total Futures Open Interest ($) | `GET /api/v1/market/overview` | Multi-venue Aggregator (Binance + Bybit + OKX) | 5 seconds | **OBSERVED** | **COMPLETE** |
| **HomeScreen** | 24h Global Trading Volume ($) | `GET /api/v1/market/overview` | Aggregated 24h quote volume across major venues | 5 seconds | **OBSERVED** | **COMPLETE** |
| **HomeScreen** | Fear & Greed Index Dial | `GET /api/v1/sentiment/fear-greed`| Alternative.me verified real-time index API | 15 minutes | **OBSERVED** | **COMPLETE** |
| **HomeScreen** | Contract Radar Surges | `GET /api/v1/radar/contracts` | Statistical OI & Volume Z-score outlier detector | 10 seconds | **CALCULATED** | **COMPLETE** |
| **HomeScreen** | Top Gainers & Losers Horizontal Strip | `GET /api/v1/rankings?type=gainers`| Exchange 24h price change percentage sort | 5 seconds | **OBSERVED** | **COMPLETE** |
| **HomeScreen** | Watchlist Ticker Cards | `GET /api/v1/market/tickers` | Real exchange bookTicker & 24hr tickers via Room cache | 1 second | **OBSERVED** | **COMPLETE** |
| **MarketsScreen** | Search & Tier Filter Chips | `GET /api/v1/screener` | AssetRegistry dynamic classification (Tier-1, 2, 3) | Static / Cached | **CALCULATED** | **COMPLETE** |
| **MarketsScreen** | Sortable Table (Price, 24h Chg, OI) | `GET /api/v1/screener` | Multi-exchange normalized market stream | 3 seconds | **OBSERVED** | **COMPLETE** |
| **RankingScreen** | Volume / Funding / Gainers Tabs | `GET /api/v1/rankings` | Aggregated rank comparator across all instruments | 10 seconds | **OBSERVED** | **COMPLETE** |
| **AssetDetailScreen**| Real-Time OHLCV Candlestick Chart | `GET /api/v1/market/candles/{sym}`| High-precision exchange klines (1m, 5m, 1h, 1d) | 1 second | **OBSERVED** | **COMPLETE** |
| **AssetDetailScreen**| 24h High, Low, Quote Volume | `GET /api/v1/market/ticker/{sym}` | Exchange 24hr rolling window statistics | 1 second | **OBSERVED** | **COMPLETE** |
| **AssetDetailScreen**| Live Execution Trade Tape | `GET /api/v1/market/trades/{sym}` | Aggregated recent execution stream with buy/sell tag | 500 ms | **OBSERVED** | **COMPLETE** |
| **OrderBookScreen** | Level 2 Depth Ladder & Microprice | `GET /api/v1/market/orderbook/{sym}`| Synchronized orderbook bids/asks + Microprice formula | 500 ms | **CALCULATED** | **COMPLETE** |
| **OrderBookScreen** | Orderbook Imbalance (OBI) Gauge | `GET /api/v1/market/orderbook/{sym}`| Normalized top 10bps depth imbalance | 500 ms | **CALCULATED** | **COMPLETE** |
| **AIPredictionScreen**| Forecast Direction & Probability | `GET /api/v1/predictions/{sym}` | `services/prediction.py` (Mixture of Experts) | 1 minute | **MODEL_OUTPUT** | **COMPLETE** |
| **AIPredictionScreen**| P10, P50, P90 Price Quantile Fan | `GET /api/v1/predictions/{sym}` | Volatility step-sigma parametric quantile formula | 1 minute | **MODEL_OUTPUT** | **COMPLETE** |
| **AIPredictionScreen**| Feature Attribution (SHAP Bars) | `GET /api/v1/predictions/{sym}` | Relative importance weights across active experts | 1 minute | **MODEL_OUTPUT** | **COMPLETE** |
| **AIPredictionScreen**| Market Regime Context Card | `GET /api/v1/predictions/{sym}` | Realized volatility & Trend classification engine | 1 minute | **CALCULATED** | **COMPLETE** |
| **FundingScreen** | Heatmap Matrix by Exchange | `GET /api/v1/derivatives/funding` | Binance, Bybit, OKX live premium index rates | 30 seconds | **OBSERVED** | **COMPLETE** |
| **FundingScreen** | Predicted Next Funding Rate | `GET /api/v1/derivatives/funding` | Time-decay interest rate + 8h clamp projection | 30 seconds | **ESTIMATED** | **COMPLETE** |
| **LiquidationsScreen**| 24h Total Liquidated Volume | `GET /api/v1/derivatives/liquidations`| Aggregated liquidation orders across all instruments | 10 seconds | **OBSERVED** | **COMPLETE** |
| **LiquidationsScreen**| Estimated Liquidation Price Clusters | `GET /api/v1/derivatives/liquidations`| Leverage leverage distribution estimation model | 1 minute | **ESTIMATED** | **COMPLETE** |
| **ETFScreen** | Daily Net Inflows / Outflows ($M) | `GET /api/v1/etf/overview` | Verified public Farside/SosoValue ETF telemetry | 1 hour | **OBSERVED** | **COMPLETE** |
| **FundFlowScreen** | Exchange Inflow / Outflow Balances | `GET /api/v1/onchain/flows` | On-chain cluster monitoring & DefiLlama balances | 15 minutes | **OBSERVED** | **COMPLETE** |
| **HolderScreen** | Whale Concentration & Top 100 Holdings| `GET /api/v1/onchain/holders` | Public blockchain distributed ledger metrics | 1 hour | **OBSERVED** | **COMPLETE** |
| **NewsScreen** | Chronological News Feed | `GET /api/v1/news` | Curated crypto market news aggregator | 5 minutes | **OBSERVED** | **COMPLETE** |
| **MacroScreen** | Macro Dominance & Economic Calendar | `GET /api/v1/events` | Economic calendar releases (CPI, FOMC rate cuts) | 1 hour | **OBSERVED** | **COMPLETE** |
| **UserCenterScreen** | Profile, Node Latency, Account Auth | `GET /api/v1/auth/me`, `/providers/status`| Canonical JWT profile & real provider health pings | Real-time | **OBSERVED** | **COMPLETE** |
| **PaperDashboardScreen**| Portfolio Balance & Realized/Unrealized PnL| Local Room + `GET /api/v1/market/tickers`| Local paper trade database marked to live prices | 1 second | **CALCULATED** | **COMPLETE** |

---

## 2. Invariant & Data Integrity Auditing

1. **Clear Semantic Labeling**: Every value displayed in the client UI is tagged as either:
   - `OBSERVED`: Direct, unmanipulated telemetry from connected exchanges (e.g. Binance/Bybit tickers, klines, depth).
   - `CALCULATED`: Deterministic mathematical derivations (e.g. OBI, Microprice, Basis bps, 24h return).
   - `ESTIMATED`: Statistical approximations clearly marked to avoid user confusion (e.g. Liquidation Heatmap clusters).
   - `MODEL_OUTPUT`: Probabilistic predictions generated by the quantitative ensemble (P10-P90 quantiles, confidence, SHAP).
2. **Zero Fake Initial State**: If the network connection is establishing, the UI displays clear Skeleton / Shimmer loading indicators, transitioning cleanly to Live data once the HTTP or WebSocket response arrives.
