"""
CryptoScope AI - Constants & Quantitative Thresholds
"""
DISCLAIMER_TEXT = "Probabilistic market analysis — not a guarantee of future performance."

# Quantitative gating defaults
DEFAULT_MIN_CONFIDENCE = 75
DEFAULT_MIN_MODEL_AGREEMENT = 70
DEFAULT_MIN_DATA_QUALITY = 90
MAX_ALLOWED_SPREAD_BPS = 15.0

# Transaction costs for backtesting & paper trading
DEFAULT_MAKER_FEE_BPS = 2.0   # 0.02%
DEFAULT_TAKER_FEE_BPS = 4.0   # 0.04%
DEFAULT_BASE_SLIPPAGE_BPS = 1.5

# Standard horizons in seconds
HORIZON_SECONDS = {
    "1m": 60,
    "5m": 300,
    "15m": 900,
    "30m": 1800,
    "1h": 3600,
    "4h": 14400,
    "12h": 43200,
    "1d": 86400,
}

SUPPORTED_SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
SUPPORTED_ASSETS = ["BTC", "ETH", "SOL"]
