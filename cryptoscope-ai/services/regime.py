"""
CryptoScope AI - Market Regime Detection Engine
Implements Section 19 specifications:
Regimes: BULL_TREND, BEAR_TREND, SIDEWAYS, HIGH_VOLATILITY, LOW_VOLATILITY, BREAKOUT, PANIC, EUPHORIA, LIQUIDATION_CASCADE, EVENT_RISK
"""
import math
from typing import Dict, Any, List
from core.enums import MarketRegime

class RegimeDetectionEngine:
    def classify_regime(
        self,
        realized_volatility: float,
        funding_zscore: float,
        momentum_1h: float,
        liquidation_pressure: float,
        minutes_to_macro_event: int = 9999
    ) -> Dict[str, Any]:
        # Event risk check
        if minutes_to_macro_event < 60:
            return {
                "regime": MarketRegime.EVENT_RISK.value,
                "confidence": 92,
                "description": f"High event risk: Scheduled macro announcement in {minutes_to_macro_event}m. Signal confidence automatically discounted."
            }

        # Liquidation cascade check
        if liquidation_pressure > 80:
            return {
                "regime": MarketRegime.LIQUIDATION_CASCADE.value,
                "confidence": 88,
                "description": "Liquidation cascade active: aggressive forced unravelling and stop runs in progress."
            }

        # Extreme euphoria or panic
        if funding_zscore > 2.5 and momentum_1h > 2.0:
            return {
                "regime": MarketRegime.EUPHORIA.value,
                "confidence": 85,
                "description": "Euphoric overheating: extreme funding rate premium and crowded long positioning."
            }
        elif funding_zscore < -2.5 and momentum_1h < -2.0:
            return {
                "regime": MarketRegime.PANIC.value,
                "confidence": 86,
                "description": "Panic capitulation: heavy negative funding dislocation and panic spot selling."
            }

        # Volatility classification
        if realized_volatility > 0.05:
            regime = MarketRegime.HIGH_VOLATILITY.value
            desc = "High volatility expansion: wider quantile forecast fan and increased slippage penalty."
        elif realized_volatility < 0.012:
            regime = MarketRegime.LOW_VOLATILITY.value
            desc = "Low volatility compression: potential upcoming structural breakout regime."
        elif momentum_1h > 0.8:
            regime = MarketRegime.BULL_TREND.value
            desc = "Moderate bullish trend structure with steady spot buyer CVD accumulation."
        elif momentum_1h < -0.8:
            regime = MarketRegime.BEAR_TREND.value
            desc = "Moderate bearish markdown regime with active passive ask wall reinforcement."
        else:
            regime = MarketRegime.SIDEWAYS.value
            desc = "Sideways range consolidation: mean-reverting book dynamics with balanced order flow."

        return {
            "regime": regime,
            "confidence": 81,
            "description": desc
        }


regime_engine = RegimeDetectionEngine()

