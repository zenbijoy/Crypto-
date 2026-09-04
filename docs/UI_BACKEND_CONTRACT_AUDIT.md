# UI → Backend Contract Audit

## Executive Summary
This document provides a complete audit of every Screen, Composable, ViewModel, Repository, DTO, API client, navigation destination, chart component, button, selector, tab, and card within the CryptoScope AI Android application. Every visible data field has been inspected, categorized by its source and status, and mapped to its required production backend endpoint, provider, refresh rate, and caching policy.

---

## Status Definitions
- **REAL**: Backed by live network calls with real market data (e.g. Binance Futures public endpoints).
- **PARTIAL**: Backed partially by live ticker data, but uses local mock/simulated calculations for certain attributes.
- **FAKE**: Hardcoded static text or simulated random mock figures displayed in UI.
- **MISSING**: UI element exists or is needed, but has no backing network endpoint or repository implementation.
- **UNAVAILABLE**: External upstream provider requires private institutional API credentials; marked as `NOT_CONFIGURED` or `DATA_UNAVAILABLE` with transparent provenance.

---

## Screen-by-Screen Component Audit

### 1. HomeScreen (`HomeScreen.kt`)
| Component / Card | Visible Field | Current Source | Status | Required Backend Endpoint | Provider | Refresh | Caching |
|---|---|---|---|---|---|---|---|
| Top Header Tabs | Market, Ranking, Feature | Local State | REAL | Navigation / filter | App local | On click | Memory |
| Search Icon | Search icon button | Navigation | REAL | `ScreenRoute.GLOBAL_SEARCH` | Local | On click | N/A |
| Notifications Icon | Bell badge ("3") | Local State | PARTIAL | `GET /api/v1/news?category=All` | Backend | 30s | 15s |
| Referral Promo Banner | "CryptoScope Referral Program" | Static asset | REAL | Static Promo Display | Local | Static | Static |
| Fear & Greed Quick Pill | "Fear and Greed 70", "Greed" | Hardcoded static string | FAKE | `GET /api/v1/sentiment/fear-greed` | Alternative.me / Backend | 60s | 300s |
| Total Futures OI Card | "106.9B", "▼ 1.05%" | Hardcoded static string | FAKE | `GET /api/v1/market/overview` | Binance / Bybit / OKX Aggregator | 5s | 3s |
| 24H Futures Volume Card | "141.3B", "▼ 14.53%" | Hardcoded static string | FAKE | `GET /api/v1/market/overview` | Binance / Bybit / OKX Aggregator | 5s | 3s |
| Longs Shorts Ratio Card | "1.23", "▲ 20.00%" | Hardcoded static string | FAKE | `GET /api/v1/market/overview` | Binance Futures Top Accounts | 10s | 5s |
| Liquidation (24H) Card | "L $120.5M", "S $71.5M" | Hardcoded static string | FAKE | `GET /api/v1/market/overview` | Liquidation Aggregator | 5s | 3s |
| Contract Radar Banner | "Contract Radar · BTC Liquidation Pool at 77.2K", score "82" | Hardcoded static string | FAKE | `GET /api/v1/radar/contracts` | Liquidation Radar Engine | 15s | 10s |
| 8-Grid Shortcuts | AI Analyze, Fund Flow, Aggregated Book, Visual Screener, Liquidation Map, ETF Flow, Funding Heatmap, More Hub | Navigation Intents | REAL | Internal Navigation Router | Compose | Instant | Memory |
| Sentiment Card | "70", "Greed" | Hardcoded static string | FAKE | `GET /api/v1/sentiment/fear-greed` | Alternative.me / Backend | 60s | 300s |
| BTC Dominance Card | "59.73%", "▼ 0.02%" | Hardcoded static string | FAKE | `GET /api/v1/market/btc-dominance` | CoinGecko / Global Engine | 60s | 60s |
| Altcoin Season Card | "51 / 100", "Alt Season" | Hardcoded static string | FAKE | `GET /api/v1/market/altcoin-season` | Alt Season Index Engine | 300s | 300s |
| Liquidation Dual-Axis Chart | "$192.12M", "▲ 30.84%", Price Line, Long Bars, Short Bars | Hardcoded Canvas loop | FAKE | `GET /api/v1/liquidations/history/{symbol}` | Liquidation Engine | 15s | 10s |
| Longs VS Shorts Card | Timeframe buttons (5m, 1H, 4H, 24H) | Local state | REAL | Query parameter | Local | On click | Memory |
| Taker Buy/Sell Ratio | "BTC Taker Buy/Sell Ratio: 0.95" | Hardcoded static string | FAKE | `GET /api/v1/orderflow/{symbol}` | Binance / Bybit Taker Flow | 5s | 3s |
| Long/Short Split Bar | "Longs 48.67%", "Shorts 51.33%" | Hardcoded weights | FAKE | `GET /api/v1/market/futures/aggregate` | Binance Futures Top Ratio | 10s | 5s |
| Market Movers Tabs | "OI Chg", "Funding Rate", "Gainers", "Losers" | Local state | REAL | `GET /api/v1/rankings` | Ranking Engine | 10s | 5s |
| Market Movers Coin List | Symbol, Price, 24H Chg, OI | Repository `getMarkets()` | PARTIAL | `GET /api/v1/markets` | Binance 24hr Tickers | 3s | 2s |

---

### 2. FearAndGreedScreen (`FearAndGreedScreen.kt`)
| Component / Card | Visible Field | Current Source | Status | Required Backend Endpoint | Provider | Refresh | Caching |
|---|---|---|---|---|---|---|---|
| Speedometer Arc Gauge | Score "70", Label "Greed" | Hardcoded static | FAKE | `GET /api/v1/sentiment/fear-greed` | Alternative.me / Backend | 60s | 300s |
| Historical Compare Card | "Yesterday Greed-61", "7d ago Greed-73", "30d ago Fear-28" | Hardcoded list | FAKE | `GET /api/v1/sentiment/fear-greed` | Alternative.me API | 60s | 300s |
| Year Stats Card | "Year High 2026-08-24 Greed-74", "Year Low 2026-02-07 Extreme Fear-5" | Hardcoded list | FAKE | `GET /api/v1/sentiment/fear-greed` | Alternative.me 365d | 300s | 3600s |
| Historical Chart | Canvas points & BTC price overlay | Hardcoded dummy points | FAKE | `GET /api/v1/sentiment/fear-greed/history` | Alternative.me + Binance BTC | 300s | 600s |
| Timeline Selectors | 30d, 90d, 1y, All | Local state | REAL | Query `range=` | Local | On click | Memory |

---

### 3. DerivativesScreen (`DerivativesScreen.kt`)
| Component / Card | Visible Field | Current Source | Status | Required Backend Endpoint | Provider | Refresh | Caching |
|---|---|---|---|---|---|---|---|
| Current Funding Rate Card | Current Funding Rate %, 8h countdown | Simulated formula | PARTIAL | `GET /api/v1/assets/{symbol}/derivatives` | Binance Premium Index | 5s | 3s |
| Multi-Venue Funding Card | Binance, Bybit, OKX funding rates | Simulated values | PARTIAL | `GET /api/v1/funding/heatmap` | CrossExchangeFundingEngine | 10s | 5s |
| Open Interest Summary | Total OI USD, 24h change % | Simulated calculation | PARTIAL | `GET /api/v1/market/futures/aggregate` | CrossExchangeOI Engine | 5s | 3s |
| Basis Card | Annualized Basis %, Mark vs Index | Simulated calculation | PARTIAL | `GET /api/v1/assets/{symbol}/derivatives` | CrossExchangePriceEngine | 5s | 3s |
| Order Flow Analytics | CVD, Delta, Buy/Sell Ratio | Simulated calculation | PARTIAL | `GET /api/v1/orderflow/{symbol}` | OrderFlowEngineV2 | 3s | 1s |
| Options Analytics | Max Pain, Put/Call Ratio, 25 Delta Skew | Hardcoded / Mock | UNAVAILABLE | `GET /api/v1/assets/{symbol}/derivatives` | Deribit / NOT_CONFIGURED | 30s | 60s |

---

### 4. LiquidationsScreen (`LiquidationsScreen.kt`)
| Component / Card | Visible Field | Current Source | Status | Required Backend Endpoint | Provider | Refresh | Caching |
|---|---|---|---|---|---|---|---|
| Mode Toggle | Map vs Heatmap | Local state | REAL | UI View Switch | Compose | Instant | Memory |
| Symbol Pill & Timeframe | Binance/BTCUSDT, 12h, 1d, 3d, 7d | Local state | REAL | Query parameters | Compose | Instant | Memory |
| Radar Alert Badge | "Radar: 6 Liqs" | Hardcoded static | FAKE | `GET /api/v1/liquidations/radar/{symbol}` | LiquidationRadarService | 10s | 5s |
| Overview Metrics | Total Long Liq, Total Short Liq | Hardcoded static | FAKE | `GET /api/v1/liquidations/{symbol}` | LiquidationEngine | 5s | 3s |
| Liquidation Map Bars | Long vs Short cumulative pools | Hardcoded bar values | FAKE | `GET /api/v1/liquidations/map/{symbol}` | LiquidationEstimationEngine | 15s | 10s |
| Liquidation Heatmap Matrix | 2D intensity grid, Price candles | Hardcoded canvas grid | FAKE | `GET /api/v1/liquidations/heatmap/{symbol}` | LiquidationHeatmapEngine | 15s | 10s |
| Real-time Observed Feed | Recent liquidation trade stream | Simulated items | PARTIAL | `GET /api/v1/liquidations/{symbol}` & WS | Binance Liq WebSocket | 1s | Stream |

---

### 5. AIPredictionScreen (`AIPredictionScreen.kt`)
| Component / Card | Visible Field | Current Source | Status | Required Backend Endpoint | Provider | Refresh | Caching |
|---|---|---|---|---|---|---|---|
| Model Header | Symbol, Model Tier, Data Quality | Local repository math | PARTIAL | `GET /api/v1/predictions/{symbol}` | ML Serving & MoE Combiner | 5s | 3s |
| Horizon Selector | 1m, 5m, 15m, 30m, 1h, 4h, 12h, 1d, 3d, 7d | Local state | REAL | Query parameter | Compose | Instant | Memory |
| Direction Probabilities | P_up, P_side, P_down | Local math | PARTIAL | `GET /api/v1/predictions/{symbol}` | LearnedMoE & Quantiles | 5s | 3s |
| Forecast Fan Chart | P10, P25, P50, P75, P90 envelopes | Local extrapolation | PARTIAL | `GET /api/v1/predictions/{symbol}` | Deep Quantile Ensemble | 5s | 3s |
| Explainability Factors | SHAP feature attributions | Local mock list | PARTIAL | `GET /api/v1/predictions/{symbol}` | Explainability Engine | 5s | 3s |
| Abstention Banner | Abstain status, reason, risk veto | Local heuristic | PARTIAL | `GET /api/v1/predictions/{symbol}` | UncertaintyEngineV2 & KillSwitch | 5s | 3s |

---

### 6. OrderBookScreen (`OrderBookScreen.kt`)
| Component / Card | Visible Field | Current Source | Status | Required Backend Endpoint | Provider | Refresh | Caching |
|---|---|---|---|---|---|---|---|
| Aggregated L2 Depth | Bids & Asks, Depth bars | Binance depth (single) | PARTIAL | `GET /api/v1/orderbook/aggregated/{symbol}` | CrossExchangeOB Aggregator | 1s | 0.5s |
| Microstructure Summary | Mid price, Spread bps, Imbalance | Single exchange | PARTIAL | `GET /api/v1/orderbook/aggregated/{symbol}` | OrderBookFeatureEngine | 1s | 0.5s |
| Venue Distribution | Binance %, Bybit %, OKX % | Hardcoded / Mock | FAKE | `GET /api/v1/orderbook/aggregated/{symbol}` | CrossExchange Aggregator | 2s | 1s |

---

### 7. OnChainScreen (`OnChainScreen.kt`)
| Component / Card | Visible Field | Current Source | Status | Required Backend Endpoint | Provider | Refresh | Caching |
|---|---|---|---|---|---|---|---|
| Exchange Netflow | Netflow BTC, Inflow/Outflow label | Local mock repository | FAKE | `GET /api/v1/onchain/{asset}/holders` | Public Node / Blockchain RPC | 60s | 120s |
| Whale Deposits | Large transaction count | Local mock repository | FAKE | `GET /api/v1/onchain/{asset}/whales` | Whale Analytics Engine | 60s | 120s |
| Miner Reserve | Miner reserve change | Local mock repository | FAKE | `GET /api/v1/onchain/{asset}/holders` | Blockchain Explorer RPC | 120s | 300s |
| Active Addresses | 24h active address count | Local mock repository | FAKE | `GET /api/v1/onchain/{asset}/holders` | Mempool / Chain RPC | 60s | 120s |
| Top Address Concentration | Top 10, Top 20, Top 50 share | Local mock values | FAKE | `GET /api/v1/onchain/{asset}/top-addresses` | Public Ledger Analytics | 300s | 600s |
| Whale Address Table | Address, Balance, 30d Chg, Label | Local mock table | FAKE | `GET /api/v1/onchain/{asset}/whales` | Whale Tracker Engine | 60s | 120s |

---

### 8. NewsScreen (`NewsScreen.kt`)
| Component / Card | Visible Field | Current Source | Status | Required Backend Endpoint | Provider | Refresh | Caching |
|---|---|---|---|---|---|---|---|
| News Tabs & Category Filter | News flash, AI Analysis, All/Liq/Whale | Local state | REAL | Query parameter | Compose | Instant | Memory |
| News Feed Cards | Title, content, timestamp, tag, alert | Hardcoded list | FAKE | `GET /api/v1/news` | NewsEngine & NLP Classifier | 30s | 15s |
| Sentiment Gauge | Asset sentiment breakdown | Hardcoded / Mock | FAKE | `GET /api/v1/news/sentiment/{symbol}` | SentimentFeatureEngine | 60s | 30s |

---

### 9. MacroScreen (`MacroScreen.kt`) & LevelsScreen (`LevelsScreen.kt`)
| Component / Card | Visible Field | Current Source | Status | Required Backend Endpoint | Provider | Refresh | Caching |
|---|---|---|---|---|---|---|---|
| Macro Rates | 10Y Yield, 2Y Yield, Spread, DXY | Hardcoded in mock | PARTIAL | `GET /api/v1/macro/state` | MacroEngine | 60s | 60s |
| Economic Calendar | FOMC, CPI, Non-Farm Payrolls | Hardcoded in mock | PARTIAL | `GET /api/v1/events` | EventEngine | 300s | 300s |
| Support/Resistance Levels | Key levels, Pivot points | Simulated values | PARTIAL | `GET /api/v1/assets/{symbol}/overview` | Technical Levels Engine | 15s | 10s |

---

### 10. Alerts & User Center Screens
| Component / Card | Visible Field | Current Source | Status | Required Backend Endpoint | Provider | Refresh | Caching |
|---|---|---|---|---|---|---|---|
| Alerts List | User created price/liq/funding alerts | In-memory mock list | PARTIAL | `GET /api/v1/alerts` | Alert Engine & Repository | On load | 5s |
| Create / Edit Alert | Threshold, trigger condition, asset | UI Form | PARTIAL | `POST /api/v1/alerts` | Alert Service | On submit | Instant |
| User Profile | Username, Tier, API keys, Referral | Local SharedPreferences | PARTIAL | `GET /api/v1/users/me` | Auth & User Service | On load | 60s |
| Watchlist | Starred assets list | In-memory set | PARTIAL | `GET /api/v1/watchlist` | Watchlist Service | On load | 5s |
| System Health | Service uptime, engine latencies, DLQ | Simulated health | PARTIAL | `GET /health`, `/mlops/serving/status` | Quantitative Gateway | 5s | 2s |

---

## Remediation Plan
1. Implement all missing endpoints in FastAPI backend with real multi-venue aggregation, mathematical models, and transparent provenance.
2. Build full data contracts with zero fabricated financial data.
3. For institutional data requiring private credentials (e.g. proprietary options order flow or private node indexers), return explicit transparent states (`NOT_CONFIGURED` or `DATA_UNAVAILABLE`) with full provenance metadata.
4. Update and expand the backend router architecture to serve all Android components seamlessly.
