# CryptoScope AI — Configuration Reference

**Purpose**: Consolidated, authoritative reference for all runtime configuration variables, default behaviors, validation rules, and deployment profiles.  
**Implementation**: `core/config.py` (Pydantic `Settings` class reading from environment and `.env`)  
**Auditor**: DevOps & Security Architecture Engineer  

---

## 1. Unified Environment Configuration Specification

| Variable Name | Type | Default Value | Production Recommended | Description & System Scope |
|---|---|---|---|---|
| `PROJECT_NAME` | `str` | `"CryptoScope AI"` | `"CryptoScope AI"` | System branding across API docs and logging |
| `ENVIRONMENT` | `str` | `"development"` | `"production"` | Runtime profile (`development`, `staging`, `production`) |
| `API_V1_STR` | `str` | `"/api/v1"` | `"/api/v1"` | Canonical API route prefix for all endpoints |
| `SECRET_KEY` | `str` | `"cryptoscope_super_secure_jwt_secret_key_2026"` | `Generate secure 256-bit key` | Symmetric key for HMAC-SHA256 JWT encoding |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `int` | `10080` (7 days) | `1440` (24 hours) | JWT bearer token expiration window |
| `CORS_ORIGINS` | `List[str]` | `["http://localhost:3000", ...]` | Explicit production domains | Allowed origins for browser CORS enforcement (zero wildcard in prod) |
| `ALLOWED_HOSTS` | `List[str]` | `["*"]` | Domain names / IPs | Trusted host HTTP header validation filter |
| `DATABASE_URL` | `str` | `"sqlite+aiosqlite:///./cryptoscope.db"` | `"postgresql+asyncpg://user:pass@host:5432/cryptoscope"` | Async SQLAlchemy database connection string |
| `REDIS_URL` | `Optional[str]` | `None` | `"redis://:pass@host:6379/0"` | Redis Streams and distributed cache connection string |
| `MLFLOW_TRACKING_URI` | `Optional[str]` | `None` | `"http://mlflow.internal:5000"` | Remote MLflow tracking server for model registry artifacts |
| `TELEGRAM_BOT_TOKEN` | `Optional[str]` | `None` | `Secured via Secret Manager` | Telegram Bot API token for `/predict` and alerts bot |
| `BINANCE_ENABLED` | `bool` | `True` | `True` | Master enable flag for Binance USD-M market data ingestion |
| `BYBIT_ENABLED` | `bool` | `True` | `True` | Master enable flag for Bybit Linear V5 market data ingestion |
| `OKX_ENABLED` | `bool` | `True` | `True` | Master enable flag for OKX Swap V5 market data ingestion |
| `COINBASE_ENABLED` | `bool` | `True` | `True` | Enable flag for Coinbase USD reference spot pairs |
| `KRAKEN_ENABLED` | `bool` | `True` | `True` | Enable flag for Kraken reference spot data |
| `HYPERLIQUID_ENABLED` | `bool` | `True` | `True` | Enable flag for Hyperliquid DEX perpetual data |
| `COINANK_ENABLED` | `bool` | `False` | `False` (Unless authorized key) | Flag for CoinAnk proprietary enrichment (Graceful degradation) |
| `COINANK_API_KEY` | `Optional[str]` | `None` | `Secured via Secret Manager` | API key for CoinAnk provider if enabled |
| `COINGECKO_ENABLED` | `bool` | `True` | `True` | Master enable flag for CoinGecko asset metadata and market caps |
| `COINGECKO_API_KEY` | `Optional[str]` | `None` | `Secured via Secret Manager` | CoinGecko Pro API key (optional, falls back to public API) |
| `COINMETRICS_ENABLED` | `bool` | `True` | `True` | On-chain reference metrics provider |
| `DEFILLAMA_ENABLED` | `bool` | `True` | `True` | DeFi and stablecoin TVL metrics provider |
| `FRED_ENABLED` | `bool` | `False` | `True` (With key) | Federal Reserve Economic Data (FRED) macro metrics |
| `FRED_API_KEY` | `Optional[str]` | `None` | `Secured via Secret Manager` | API key for St. Louis Fed FRED data |
| `DEFAULT_CONFIDENCE_THRESHOLD` | `int` | `75` | `80` | Minimum ensemble confidence score to mark signal actionable |
| `DATA_QUALITY_MIN_SCORE` | `int` | `90` | `92` | Minimum data quality score required to authorize prediction |
| `MAX_SPREAD_BPS_LIMIT` | `float` | `15.0` | `12.0` | Maximum bid/ask spread (bps) before abstaining from trading |
| `WS_HEARTBEAT_INTERVAL_SECONDS` | `int` | `15` | `15` | Ping/pong heartbeat interval for connected WebSocket clients |

---

## 2. Docker & Compose Integration

In containerized deployments, all variables are supplied via standard Docker environment variables or orchestration secrets (Kubernetes Secrets, Cloud Run Environment Variables, or HashiCorp Vault):

```yaml
version: '3.8'
services:
  api:
    image: cryptoscope/api:latest
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql+asyncpg://crypto_app:${DB_PASS}@timescaledb:5432/cryptoscope
      - REDIS_URL=redis://:${REDIS_PASS}@redis:6379/0
      - SECRET_KEY=${JWT_SECRET_KEY}
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - CORS_ORIGINS=["https://cryptoscope.ai","https://app.cryptoscope.ai"]
    ports:
      - "8000:8000"
    restart: always
```

---

## 3. Secret Hygiene Principles

1. **Zero Hardcoded Secrets**: No sensitive JWT signing keys, database passwords, or provider API keys are committed in source code.
2. **Graceful Degradation**: Optional external providers (CoinAnk, FRED) degrade gracefully to public or internal fallback baselines if their respective keys are absent.
