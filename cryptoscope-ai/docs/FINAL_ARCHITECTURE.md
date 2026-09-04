# CryptoScope AI — Final Production Architecture

**System Architecture & End-to-End Enterprise Specification**  
**Classification**: Unified System Blueprint  

---

## 1. System Topology Overview

CryptoScope AI is an institutional-grade crypto market intelligence, orderflow analytics, and probabilistic forecasting ecosystem. The target architecture enforces strict segregation of concerns:

- **Mobile Client**: Modern Android application built in Kotlin and Jetpack Compose (Material 3). Interacts exclusively with the FastAPI backend via HTTPS.
- **Edge Layer**: Cloudflare provides SSL/TLS termination, rate limiting, DDoS mitigation, and global DNS routing.
- **Identity Provider**: Supabase Auth handles user registration, password resets, email verification, and OAuth. Returns signed JWTs to the client.
- **API Gateway**: Canonical FastAPI server (`cryptoscope-ai/apps/api/main.py`) exposed strictly under the `/api/v1` prefix. Verifies Supabase tokens server-side.
- **Relational & Time-Series DB**: PostgreSQL with TimescaleDB extension. Segregated schemas (`product`, `quant`, `mlops`, `audit`).
- **In-Memory Cache & Streams**: Redis instance managing realtime tickers, orderbook depth, online feature store, and event streams.
- **Object Storage**: S3-compatible cloud storage (Cloudflare R2, AWS S3, or MinIO for local development) storing partitioned Parquet datasets and ML artifacts.
- **MLOps Platform**: MLflow handles experiment tracking, model registry, artifact storage, and governance stages (`EXPERIMENTAL`, `CANDIDATE`, `PRODUCTION`).
- **Notification Services**: Firebase Cloud Messaging (FCM) for low-latency Android mobile push notifications; Telegram Bot for quantitative alerts and interactive `/predict` commands.

---

## 2. Component Responsibility Matrix

| Subsystem | Technology Stack | Primary Responsibilities | Data Retention / State |
|---|---|---|---|
| **Android Client** | Kotlin, Compose, Room, Retrofit | User presentation, chart visualization, offline caching, push notifications | Local Room cache + SQLite |
| **Auth Provider** | Supabase Auth (GoTrue) | User credential storage, OAuth authentication, JWT issuance | Supabase Managed |
| **API Gateway** | FastAPI, Pydantic, Uvicorn | Request validation, auth verification, endpoint routing, WebSocket multiplexing | Stateless |
| **Product Database** | PostgreSQL 16 | User profiles, watchlists, alert rules, notification preferences, device tokens | Persistent ACID |
| **Quant Database** | TimescaleDB | Candles, trades, L2 snapshots, funding rates, open interest, predictions | Hypertable chunks with compression & retention |
| **Cache & Streams** | Redis 7 | Latest market quotes, microprice, feature vectors, streaming trade queues | In-memory with RDB/AOF persistence |
| **Object Store** | Cloudflare R2 / AWS S3 | Partitioned historical Parquet data, model checkpoints, backtest reports | Cold & Warm cloud storage |
| **Model Registry** | MLflow | Model version tracking, metrics, hyperparameter logging, deployment staging | Metadata in Postgres, artifacts in S3 |
| **Push Notifications** | Firebase Admin SDK (FCM) | Targeted device push notifications for trading signals and alerts | Ephemeral delivery |
| **Telegram Bot** | Python `python-telegram-bot` / httpx | Remote community queries, `/predict` commands, threshold alerts | Stateless bridge |
