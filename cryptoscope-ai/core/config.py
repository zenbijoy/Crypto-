"""
CryptoScope AI - Core Configuration & Settings
Universal multi-provider crypto market intelligence configuration.
"""
from pydantic_settings import BaseSettings
from typing import List, Dict, Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "CryptoScope AI"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "cryptoscope_super_secure_jwt_secret_key_2026"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Tier-1 Deep Coverage Assets (BTC, ETH, SOL, DOGE)
    TIER1_ASSETS: List[str] = ["BTC", "ETH", "SOL", "DOGE"]
    DEFAULT_QUOTE_CURRENCIES: List[str] = ["USDT", "USDC", "USD"]
    
    # Provider Enable Flags
    BINANCE_ENABLED: bool = True
    BYBIT_ENABLED: bool = True
    OKX_ENABLED: bool = True
    COINBASE_ENABLED: bool = True
    KRAKEN_ENABLED: bool = True
    HYPERLIQUID_ENABLED: bool = True
    
    # Optional Providers (Graceful degradation when disabled or key missing)
    COINANK_ENABLED: bool = False
    COINANK_API_KEY: Optional[str] = None
    COINGECKO_ENABLED: bool = True
    COINGECKO_API_KEY: Optional[str] = None
    COINMETRICS_ENABLED: bool = True
    DEFILLAMA_ENABLED: bool = True
    FRED_ENABLED: bool = False
    FRED_API_KEY: Optional[str] = None
    
    # Quantitative Risk & Quality Thresholds
    DEFAULT_CONFIDENCE_THRESHOLD: int = 75
    DATA_QUALITY_MIN_SCORE: int = 90
    MAX_SPREAD_BPS_LIMIT: float = 15.0
    WS_HEARTBEAT_INTERVAL_SECONDS: int = 15
    
    # Environment & CORS Configuration
    ENVIRONMENT: str = "production"
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        "https://cryptoscope.ai",
        "https://app.cryptoscope.ai"
    ]
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Database & Cache
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/cryptoscope"
    REDIS_URL: str = "redis://localhost:6379/0"
    MLFLOW_TRACKING_URI: Optional[str] = "http://localhost:5000"
    TELEGRAM_BOT_TOKEN: Optional[str] = None

    # Exchange Provider Base URLs
    BINANCE_BASE_URL: str = "https://api.binance.com"
    BYBIT_BASE_URL: str = "https://api.bybit.com"
    OKX_BASE_URL: str = "https://www.okx.com"

    # Supabase Auth Configuration
    SUPABASE_URL: Optional[str] = None
    SUPABASE_ANON_KEY: Optional[str] = None
    SUPABASE_JWKS_URL: Optional[str] = None
    SUPABASE_JWT_SECRET: Optional[str] = None

    # Firebase FCM Configuration
    FIREBASE_PROJECT_ID: Optional[str] = None
    FIREBASE_CREDENTIALS_PATH: Optional[str] = None

    # Object Storage (S3 / Cloudflare R2 / MinIO)
    OBJECT_STORAGE_PROVIDER: str = "s3"  # "s3", "r2", "minio"
    S3_ENDPOINT: Optional[str] = None
    S3_BUCKET: str = "cryptoscope-data"
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None
    S3_REGION: str = "us-east-1"

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"

settings = Settings()
