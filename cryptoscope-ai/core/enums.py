"""
CryptoScope AI - Canonical Domain Enums
Master specification enums across market types, asset coverage tiers, providers, regimes, and risk states.
"""
from enum import Enum

class AssetTier(str, Enum):
    TIER_1 = "TIER_1"  # Deep coverage: BTC, ETH, SOL, DOGE
    TIER_2 = "TIER_2"  # High-liquidity crypto (BNB, XRP, ADA, AVAX, LINK, SUI, etc.)
    TIER_3 = "TIER_3"  # All supported discovered assets

class MarketType(str, Enum):
    SPOT = "SPOT"
    PERPETUAL = "PERPETUAL"
    FUTURE = "FUTURE"
    OPTION = "OPTION"
    INDEX = "INDEX"
    REFERENCE = "REFERENCE"

class ContractType(str, Enum):
    LINEAR = "LINEAR"                      # USDT / USDC settled
    INVERSE = "INVERSE"                    # Coin settled
    DELIVERY_LINEAR = "DELIVERY_LINEAR"
    DELIVERY_INVERSE = "DELIVERY_INVERSE"
    CALL = "CALL"
    PUT = "PUT"
    SPOT = "SPOT"

class Provider(str, Enum):
    BINANCE = "BINANCE"
    BYBIT = "BYBIT"
    OKX = "OKX"
    COINBASE = "COINBASE"
    KRAKEN = "KRAKEN"
    HYPERLIQUID = "HYPERLIQUID"
    COINANK = "COINANK"
    COINGECKO = "COINGECKO"
    COINMETRICS = "COINMETRICS"
    DEFILLAMA = "DEFILLAMA"
    FRED = "FRED"

class Horizon(str, Enum):
    H1M = "1m"
    H3M = "3m"
    H5M = "5m"
    H15M = "15m"
    H30M = "30m"
    H1H = "1h"
    H2H = "2h"
    H4H = "4h"
    H6H = "6h"
    H12H = "12h"
    H1D = "1d"
    H1W = "1w"

class Direction(str, Enum):
    UP = "UP"
    DOWN = "DOWN"
    SIDEWAYS = "SIDEWAYS"

class TradingSignal(str, Enum):
    STRONG_LONG = "STRONG LONG"
    LONG = "LONG"
    NEUTRAL_NO_TRADE = "NEUTRAL / NO-TRADE"
    SHORT = "SHORT"
    STRONG_SHORT = "STRONG SHORT"

class MarketRegime(str, Enum):
    BULL_TREND = "BULL_TREND"
    BEAR_TREND = "BEAR_TREND"
    SIDEWAYS = "SIDEWAYS"
    HIGH_VOLATILITY = "HIGH_VOLATILITY"
    LOW_VOLATILITY = "LOW_VOLATILITY"
    BREAKOUT = "BREAKOUT"
    PANIC = "PANIC"
    EUPHORIA = "EUPHORIA"
    LIQUIDATION_CASCADE = "LIQUIDATION_CASCADE"
    EVENT_RISK = "EVENT_RISK"
    DELEVERAGING = "DELEVERAGING"

class RiskDecision(str, Enum):
    ALLOW = "ALLOW"
    REDUCE = "REDUCE"
    REJECT = "REJECT"

class ModelStage(str, Enum):
    EXPERIMENTAL = "EXPERIMENTAL"
    VALIDATED = "VALIDATED"
    CANDIDATE = "CANDIDATE"
    SHADOW = "SHADOW"
    PAPER = "PAPER"
    PRODUCTION = "PRODUCTION"
    RETIRED = "RETIRED"

class CircuitBreakerState(str, Enum):
    CLOSED = "CLOSED"      # Healthy normal operation
    OPEN = "OPEN"          # Provider failing, requests blocked/short-circuited
    HALF_OPEN = "HALF_OPEN"  # Testing canary probe requests

class BackfillStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    RETRYING = "RETRYING"
    COMPLETED = "COMPLETED"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"
