"""
CryptoScope AI - Cross-Exchange Funding Engine
Calculates cross-exchange funding rates, dispersion, divergence z-scores,
velocity, acceleration, and identifies crowded positioning or arbitrage dislocations.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import numpy as np


class CrossExchangeFundingState(BaseModel):
    canonical_symbol: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    venue_rates: Dict[str, float]  # provider -> 8h funding rate (e.g. 0.0001 = 0.01%)
    annualized_rates: Dict[str, float]  # provider -> annualized % (rate * 3 * 365 * 100)
    
    # Aggregated Stats
    mean_funding_rate: float
    median_funding_rate: float
    funding_dispersion: float  # std dev across venues
    funding_divergence: float  # max - min rate
    funding_z_score: float     # rolling divergence z-score
    
    # Dynamics
    velocity: float = 0.0      # rate change per interval
    acceleration: float = 0.0  # velocity change per interval
    
    # Regime
    regime: str  # EXTREME_POSITIVE_CROWDED_LONG, MODERATE_POSITIVE, NEUTRAL, MODERATE_NEGATIVE, EXTREME_NEGATIVE_CROWDED_SHORT, ARBITRAGE_DISLOCATION
    arbitrage_dislocation: bool
    sentiment_bias: str  # BULLISH_CROWDING, BEARISH_CROWDING, BALANCED


class CrossExchangeFundingEngine:
    def __init__(self, z_window: int = 40):
        self.z_window = z_window
        self._history: List[float] = []
        self._rate_history: List[float] = []

    def compute(self, canonical_symbol: str, venue_fundings: Dict[str, Any]) -> CrossExchangeFundingState:
        """
        venue_fundings: dict of provider -> FundingData or TickerData
        """
        rates = {}
        ann = {}
        for prov, f in venue_fundings.items():
            r = getattr(f, "funding_rate", 0.0) or 0.0
            rates[prov] = float(r)
            ann[prov] = round(float(r) * 3.0 * 365.0 * 100.0, 2)

        rate_vals = list(rates.values())
        if not rate_vals:
            rate_vals = [0.0]

        mean_r = float(np.mean(rate_vals))
        median_r = float(np.median(rate_vals))
        dispersion = float(np.std(rate_vals)) if len(rate_vals) > 1 else 0.0
        divergence = float(max(rate_vals) - min(rate_vals))

        self._history.append(divergence)
        if len(self._history) > self.z_window:
            self._history.pop(0)

        self._rate_history.append(mean_r)
        if len(self._rate_history) > self.z_window:
            self._rate_history.pop(0)

        # Z-score of divergence
        if len(self._history) >= 5:
            m = float(np.mean(self._history))
            s = float(np.std(self._history))
            z_score = float((divergence - m) / (s + 1e-6))
        else:
            z_score = 0.0

        # Velocity & Acceleration
        vel = 0.0
        acc = 0.0
        if len(self._rate_history) >= 2:
            vel = self._rate_history[-1] - self._rate_history[-2]
        if len(self._rate_history) >= 3:
            prev_vel = self._rate_history[-2] - self._rate_history[-3]
            acc = vel - prev_vel

        # Regime classification
        # Standard baseline 8h funding is 0.0001 (0.01% or ~10.95% APR)
        arb_dislocation = divergence > 0.0003  # > 3 bps spread between venues
        if arb_dislocation:
            regime = "ARBITRAGE_DISLOCATION"
            sentiment = "BALANCED"
        elif mean_r > 0.0005:  # > 0.05% per 8h (~54.7% APR)
            regime = "EXTREME_POSITIVE_CROWDED_LONG"
            sentiment = "BULLISH_CROWDING"
        elif mean_r > 0.00015:
            regime = "MODERATE_POSITIVE"
            sentiment = "BULLISH_CROWDING"
        elif mean_r < -0.0003:
            regime = "EXTREME_NEGATIVE_CROWDED_SHORT"
            sentiment = "BEARISH_CROWDING"
        elif mean_r < -0.00005:
            regime = "MODERATE_NEGATIVE"
            sentiment = "BEARISH_CROWDING"
        else:
            regime = "NEUTRAL"
            sentiment = "BALANCED"

        return CrossExchangeFundingState(
            canonical_symbol=canonical_symbol,
            venue_rates=rates,
            annualized_rates=ann,
            mean_funding_rate=round(mean_r, 6),
            median_funding_rate=round(median_r, 6),
            funding_dispersion=round(dispersion, 6),
            funding_divergence=round(divergence, 6),
            funding_z_score=round(z_score, 3),
            velocity=round(vel, 7),
            acceleration=round(acc, 7),
            regime=regime,
            arbitrage_dislocation=arb_dislocation,
            sentiment_bias=sentiment
        )
