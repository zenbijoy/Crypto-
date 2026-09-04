# CryptoScope AI — Deployment & Infrastructure Guide

**Single-VM Production, Docker Compose, Multi-Service Scaling & Local Dev**  

---

## 1. Quick Start: Local Development Environment

Spin up the entire local development stack in one command:

```bash
docker compose -f docker-compose.yml up -d
```

This launches:
- **`postgres-timescale`**: PostgreSQL 16 with TimescaleDB extension on port `5432`
- **`redis`**: Redis 7 cache and streams on port `6379`
- **`minio`**: Local S3-compatible object storage on port `9000` (Console on `9001`)
- **`mlflow`**: MLflow tracking server on port `5000`
- **`api`**: Canonical FastAPI gateway on port `8000`

---

## 2. Production Docker Compose Topology

For single-VM initial production deployment:

```yaml
version: '3.8'

services:
  api:
    image: cryptoscope/api:latest
    restart: always
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql+asyncpg://crypto_app:${DB_PASS}@timescaledb:5432/cryptoscope
      - REDIS_URL=redis://:${REDIS_PASS}@redis:6379/0
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_JWKS_URL=${SUPABASE_JWKS_URL}
      - FIREBASE_PROJECT_ID=${FIREBASE_PROJECT_ID}
      - FIREBASE_CREDENTIALS_PATH=/secrets/firebase-key.json
      - CORS_ORIGINS=["https://cryptoscope.ai","https://app.cryptoscope.ai"]
    ports:
      - "8000:8000"
    volumes:
      - ./secrets:/secrets:ro
    depends_on:
      - timescaledb
      - redis

  market-worker:
    image: cryptoscope/worker:latest
    command: python -m workers.binance_market_worker
    restart: always
    environment:
      - REDIS_URL=redis://:${REDIS_PASS}@redis:6379/0
    depends_on:
      - redis

  timescaledb:
    image: timescale/timescaledb:latest-pg16
    restart: always
    environment:
      - POSTGRES_DB=cryptoscope
      - POSTGRES_USER=crypto_app
      - POSTGRES_PASSWORD=${DB_PASS}
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "127.0.0.1:5432:5432"

  redis:
    image: redis:7-alpine
    restart: always
    command: redis-server --requirepass ${REDIS_PASS} --appendonly yes
    volumes:
      - redisdata:/data
    ports:
      - "127.0.0.1:6379:6379"

volumes:
  pgdata:
  redisdata:
```

---

## 3. Database Migration Execution

Apply schema changes using Alembic:

```bash
# Run migrations to latest revision
alembic upgrade head

# Rollback one revision if necessary
alembic downgrade -1
```
