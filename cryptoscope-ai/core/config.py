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
    
    # Database & Cache
    DATABASE_URL: str = "sqlite+aiosqlite:///./cryptoscope.db"
    REDIS_URL: Optional[str] = None

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"

settings = Settings()
