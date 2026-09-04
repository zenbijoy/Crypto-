# CryptoScope AI — Object Storage & Parquet Data Lake

**Cloudflare R2 / AWS S3 / MinIO Storage Specifications**  

---

## 1. Storage Provider Abstraction

The `ObjectStorageService` (`services/object_storage.py`) provides an S3-compliant interface compatible with:
1. **Cloudflare R2**: Production choice for zero-egress data lake and model checkpoints.
2. **AWS S3**: Enterprise cloud tier with S3 Glacier lifecycle transitions.
3. **MinIO**: Self-hosted, lightweight S3 replacement for local Docker and staging testing.

---

## 2. Partitioned Parquet Data Lake Schema

All quantitative datasets are serialized to Apache Parquet format using PyArrow / Polars, organized in hive-style partitions:

```
s3://cryptoscope-data/
├── datasets/
│   ├── provider=BINANCE/
│   │   ├── symbol=BTCUSDT/
│   │   │   ├── date=2026-09-01/
│   │   │   │   ├── candles_1m.parquet
│   │   │   │   ├── trades.parquet
│   │   │   │   └── depth_snapshots.parquet
│   │   │   └── date=2026-09-02/
│   │   └── symbol=ETHUSDT/
│   └── provider=BYBIT/
├── features/
│   └── version=v2.1/
│       └── date=2026-09-01/
│           └── features_BTCUSDT.parquet
├── models/
│   ├── artifacts/
│   │   ├── tcn_btc_1h_v3.pt
│   │   └── patchtst_multitask_v2.pt
│   └── scalers/
│       └── robust_scaler_v2.joblib
└── research/
    └── reports/
        └── backtest_run_20260901_summary.pdf
```

---

## 3. Data Integrity & Retention Rules

- **Compression**: Snappy or ZSTD compression enabled on all Parquet files.
- **Immutability**: Historical daily partition files are marked read-only with object lock / versioning.
- **Signed URL Access**: Chart snapshots and research reports are generated with time-limited presigned URLs (TTL: 3600s), ensuring zero public bucket exposure.
