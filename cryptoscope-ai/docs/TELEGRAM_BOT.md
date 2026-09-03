# CryptoScope AI — Telegram Bot Specification

---

## 🤖 Command Reference

| Command | Description |
|---|---|
| `/start` | Welcome message and platform overview |
| `/help` | Detailed list of quantitative commands and syntax |
| `/market` | Live market overview across BTC, ETH, and SOL |
| `/predict [ASSET] [HORIZON]` | Probabilistic AI forecast with fan-chart quantiles (P10–P90) and SHAP drivers |
| `/chart [ASSET]` | Generates multi-panel chart with forecast fan overlay |
| `/levels [ASSET]` | Key probabilistic support & resistance zones |
| `/funding [ASSET]` | 8h funding rate, 7-day z-score, and annualized rate |
| `/oi [ASSET]` | Open interest dynamics, velocity, and price x OI state |
| `/liquidations [ASSET]` | Liquidation heatmap clusters and pressure score |
| `/regime [ASSET]` | Current market regime classification |
| `/sentiment [ASSET]` | Crypto Fear & Greed index and news sentiment score |
| `/onchain [ASSET]` | Exchange netflows, SOPR, MVRV, and active addresses |
| `/performance [ASSET] [WINDOW]` | Out-of-sample precision, coverage, Brier score, and strategy Sharpe |
| `/alerts` | View and configure quantitative push alert triggers |
| `/status` | Infrastructure health, feed latencies, and circuit breaker status |

---

## 📜 Regulatory Mandate
Every forecast message returned by the bot must append the standardized disclaimer:
`"Probabilistic market analysis — not a guarantee of future performance."`
