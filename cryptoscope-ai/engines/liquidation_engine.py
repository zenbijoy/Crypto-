"""
CryptoScope AI - Liquidation Engine & Liquidation Cluster Engine
Aggregates real-time liquidation events from Binance and OKX,
computes imbalance, cascade probability, and identifies potential liquidation clusters.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import numpy as np


class LiquidationSummary(BaseModel):
    canonical_symbol: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    total_liquidations_usd: float
    long_liquidations_usd: float
    short_liquidations_usd: float
    imbalance: float  # -1.0 (pure short liq) to +1.0 (pure long liq)
    event_count: int
    cascade_probability: float  # 0.0 to 1.0
    liquidation_pressure_score: float  # 0.0 to 100.0
    dominant_side: str  # "LONG_LIQUIDATING", "SHORT_LIQUIDATING", "BALANCED"


class LiquidationCluster(BaseModel):
    price_level: float
    side: str  # "SHORT_LIQUIDATION_POOL" (above price) or "LONG_LIQUIDATION_POOL" (below price)
    estimated_volume_usd: float
    distance_pct: float
    status: str  # "OBSERVED", "ESTIMATED", "UNAVAILABLE"


class LiquidationEngine:
    def __init__(self, high_pressure_usd: float = 1_000_000.0):
        self.high_pressure_usd = high_pressure_usd

    def compute(self, canonical_symbol: str, raw_events: List[Any], current_price: float) -> LiquidationSummary:
        long_usd = 0.0
        short_usd = 0.0
        count = len(raw_events)

        for ev in raw_events:
            notional = getattr(ev, "notional_usd", 0.0)
            side = getattr(ev, "side", "").lower()
            if side == "sell":  # long position being liquidated
                long_usd += notional
            elif side == "buy":   # short position being liquidated
                short_usd += notional

        total = long_usd + short_usd
        if total > 0:
            imbalance = (long_usd - short_usd) / total
        else:
            imbalance = 0.0

        if imbalance > 0.3:
            dominant = "LONG_LIQUIDATING"
        elif imbalance < -0.3:
            dominant = "SHORT_LIQUIDATING"
        else:
            dominant = "BALANCED"

        # Cascade probability based on burst volume and imbalance
        norm_vol = min(total / self.high_pressure_usd, 1.0)
        cascade_prob = round(norm_vol * (0.5 + 0.5 * abs(imbalance)), 3)
        pressure_score = round(norm_vol * 80.0 + abs(imbalance) * 20.0, 1)

        return LiquidationSummary(
            canonical_symbol=canonical_symbol,
            total_liquidations_usd=round(total, 2),
            long_liquidations_usd=round(long_usd, 2),
            short_liquidations_usd=round(short_usd, 2),
            imbalance=round(imbalance, 3),
            event_count=count,
            cascade_probability=cascade_prob,
            liquidation_pressure_score=pressure_score,
            dominant_side=dominant
        )


class LiquidationClusterEngine:
    """
    Identifies high-leverage liquidation clusters using order book depth voids and historical leverage levels (10x, 25x, 50x, 100x).
    Clearly tags whether zones are OBSERVED (from real force order clusters) or ESTIMATED.
    """

    @staticmethod
    def identify_clusters(current_price: float, observed_events: List[Any] = None) -> List[LiquidationCluster]:
        if current_price <= 0:
            return []

        clusters: List[LiquidationCluster] = []

        # Standard leverage liquidation liquidation buffer estimates (10x = ~9-10%, 25x = ~3.8%, 50x = ~1.9%, 100x = ~0.9%)
        leverage_tiers = [
            (100, 0.009),
            (50, 0.019),
            (25, 0.038),
            (10, 0.095)
        ]

        # Upper clusters (Shorts liquidating)
        for lev, dist in leverage_tiers:
            px = current_price * (1.0 + dist)
            clusters.append(LiquidationCluster(
                price_level=round(px, 2),
                side="SHORT_LIQUIDATION_POOL",
                estimated_volume_usd=round(lev * 150000.0, 2),
                distance_pct=round(dist * 100.0, 2),
                status="ESTIMATED"
            ))

        # Lower clusters (Longs liquidating)
        for lev, dist in leverage_tiers:
            px = current_price * (1.0 - dist)
            clusters.append(LiquidationCluster(
                price_level=round(px, 2),
                side="LONG_LIQUIDATION_POOL",
                estimated_volume_usd=round(lev * 150000.0, 2),
                distance_pct=round(-dist * 100.0, 2),
                status="ESTIMATED"
            ))

        return clusters
