"""
CryptoScope AI - Cross-Exchange Open Interest Engine
Normalizes OI across Binance, Bybit, and OKX into true USD notional,
calculates market share, velocity, acceleration, and rolling z-scores.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import numpy as np


class OpenInterestState(BaseModel):
    canonical_symbol: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    venue_oi_usd: Dict[str, float]
    venue_market_share: Dict[str, float]  # provider -> fraction of total OI (0.0 to 1.0)
    
    total_oi_usd: float
    oi_velocity_usd: float = 0.0      # delta OI USD per update
    oi_velocity_pct: float = 0.0      # % change in OI
    oi_acceleration_usd: float = 0.0  # rate of change of velocity
    oi_z_score: float = 0.0           # rolling z-score of total OI
    oi_dispersion_usd: float = 0.0    # venue variance


class OpenInterestEngine:
    def __init__(self, z_window: int = 50):
        self.z_window = z_window
        self._oi_history: List[float] = []

    def compute(self, canonical_symbol: str, venue_ois: Dict[str, Any]) -> OpenInterestState:
        """
        venue_ois: dict of provider -> OpenInterestData
        """
        oi_usd = {}
        for prov, data in venue_ois.items():
            oi_usd[prov] = float(data.normalized_notional_usd)

        total_oi = float(sum(oi_usd.values()))
        shares = {}
        for prov, val in oi_usd.items():
            shares[prov] = round(val / total_oi, 4) if total_oi > 0 else 0.0

        dispersion = float(np.std(list(oi_usd.values()))) if len(oi_usd) > 1 else 0.0

        self._oi_history.append(total_oi)
        if len(self._oi_history) > self.z_window:
            self._oi_history.pop(0)

        # Velocity & Acceleration
        vel = 0.0
        vel_pct = 0.0
        acc = 0.0
        if len(self._oi_history) >= 2:
            vel = self._oi_history[-1] - self._oi_history[-2]
            prev_oi = self._oi_history[-2]
            vel_pct = (vel / prev_oi) * 100.0 if prev_oi > 0 else 0.0
        if len(self._oi_history) >= 3:
            prev_vel = self._oi_history[-2] - self._oi_history[-3]
            acc = vel - prev_vel

        # Z-score
        if len(self._oi_history) >= 5:
            m = float(np.mean(self._oi_history))
            s = float(np.std(self._oi_history))
            z_score = float((total_oi - m) / (s + 1e-6))
        else:
            z_score = 0.0

        return OpenInterestState(
            canonical_symbol=canonical_symbol,
            venue_oi_usd={k: round(v, 2) for k, v in oi_usd.items()},
            venue_market_share=shares,
            total_oi_usd=round(total_oi, 2),
            oi_velocity_usd=round(vel, 2),
            oi_velocity_pct=round(vel_pct, 4),
            oi_acceleration_usd=round(acc, 2),
            oi_z_score=round(z_score, 3),
            oi_dispersion_usd=round(dispersion, 2)
        )
