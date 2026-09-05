# Legacy Backend Migration Matrix

**Document Version**: 2.0  
**Status**: Canonical Migration Complete  
**Scope**: Migration of all endpoints from legacy prototype (`backend/main.py`) to canonical FastAPI gateway (`cryptoscope-ai/apps/api/`).

---

## Endpoint Mapping Matrix

| Legacy Endpoint (`backend/`) | Canonical Endpoint (`/api/v1/`) | Feature Parity | Consumer | Migration Status | Action |
|:---|:---|:---|:---|:---|:---|
| `GET /health` | `GET /health/live` & `GET /health/ready` | Full + Readiness Probe | DevOps / Kubernetes | `MIGRATED` | Use canonical health router |
| `GET /v1/market/overview` | `GET /api/v1/market/overview` | Full + Multi-venue OI & L/S | Android Home Screen | `MIGRATED` | Point Android client to canonical |
| `GET /v1/market/ticker/{symbol}` | `GET /api/v1/markets/{symbol}` | Full + Normalized Orderbook | Android Asset Detail | `MIGRATED` | Update endpoint path |
| `GET /v1/market/candles/{symbol}`| `GET /api/v1/candles/{symbol}` | Full + TimescaleDB & Redis | Android Chart Terminal | `MIGRATED` | Update endpoint path |
| `GET /v1/sentiment/fear-greed` | `GET /api/v1/sentiment/fear-greed` | Full + Historical Drift | Android Sentiment Card | `MIGRATED` | Update endpoint path |
| `GET /v1/etf/overview` | `GET /api/v1/etf/overview` | Full + Inflow/Outflow Breakdown | Android ETF Flow Pane | `MIGRATED` | Update endpoint path |
| `GET /v1/rankings` | `GET /api/v1/rankings` | Full + Volume/OI/Funding Sort | Android Markets Tab | `MIGRATED` | Update endpoint path |
| `GET /v1/screener` | `GET /api/v1/screener` | Full + Multi-tier Filters | Android Screener | `MIGRATED` | Update endpoint path |
| `GET /v1/radar/contracts` | `GET /api/v1/radar/contracts` | Full + Institutional Anomaly Engine | Android Contract Radar | `MIGRATED` | Update endpoint path |
| `GET /v1/predictions/{symbol}` | `GET /api/v1/predictions/{symbol}` | Full + Quantile Bounds P10/P90 | Android AI Prediction | `MIGRATED` | Update endpoint path |
| `GET /v1/news` | `GET /api/v1/news` | Full + Semantic Categorization | Android News Screen | `MIGRATED` | Update endpoint path |
| `GET /v1/events` | `GET /api/v1/events` | Full + High-Impact Filter | Android Events Calendar | `MIGRATED` | Update endpoint path |
| `GET /v1/providers/status` | `GET /api/v1/providers/status` | Full + Dynamic Health Checks | Android System Health | `MIGRATED` | Update endpoint path |
| `GET /v1/users/me` | `GET /api/v1/users/me` | Full + Supabase JWT Identity | Android User Profile | `MIGRATED` | Protected by Supabase Auth |
| `PATCH /v1/users/me` | `PATCH /api/v1/users/me` | Full + Product Profile Fields | Android Edit Profile | `MIGRATED` | Protected by Supabase Auth |
| `GET /v1/watchlist` | `GET /api/v1/watchlist` | Full + Real DB Persistence | Android Watchlist | `MIGRATED` | Protected by Supabase Auth |
| `POST /v1/watchlist` | `POST /api/v1/watchlist` | Full + Unique Symbol Guard | Android Watchlist | `MIGRATED` | Protected by Supabase Auth |
| `DELETE /v1/watchlist/{symbol}` | `DELETE /api/v1/watchlist/{symbol}` | Full + Soft/Hard Delete | Android Watchlist | `MIGRATED` | Protected by Supabase Auth |
| `GET /v1/alerts` | `GET /api/v1/alerts` | Full + Real Trigger Conditions | Android Alerts | `MIGRATED` | Protected by Supabase Auth |
| `POST /v1/alerts` | `POST /api/v1/alerts` | Full + Validation Rules | Android Create Alert | `MIGRATED` | Protected by Supabase Auth |
| `PATCH /v1/alerts/{id}` | `PATCH /api/v1/alerts/{id}` | Full + Toggle Active/Paused | Android Alert Details | `MIGRATED` | Protected by Supabase Auth |
| `DELETE /v1/alerts/{id}` | `DELETE /api/v1/alerts/{id}` | Full + Ownership Check | Android Alerts | `MIGRATED` | Protected by Supabase Auth |
| `POST /v1/paper/order` | `POST /api/v1/paper/order` | Full + Slippage & Margin Engine | Android Order Ticket | `MIGRATED` | Protected by Supabase Auth |
| `GET /v1/paper/positions` | `GET /api/v1/paper/positions` | Full + Live Mark Price PnL | Android Paper Dashboard | `MIGRATED` | Protected by Supabase Auth |
| `WS /v1/ws` | `WS /api/v1/ws` | Full + Multi-topic Multiplexer | Android WebSocket Client | `MIGRATED` | Update WebSocket URL |

---

## Legacy Backend Disposition

- Directory `legacy/backend/` has been disabled as a runtime service.
- Entry points in `legacy/backend/main.py` contain deprecation warnings and point to `cryptoscope-ai/apps/api/main.py`.
- No deployment scripts or Docker containers reference `legacy/backend/`.
