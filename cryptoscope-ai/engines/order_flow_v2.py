"""
CryptoScope AI - Order Flow V2 & CVD Engine
Calculates Cumulative Volume Delta (CVD), aggressive buy/sell volume,
trade intensity, large block/whale tracking, and absorption/exhaustion patterns.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import numpy as np


class OrderFlowFeatures(BaseModel):
    canonical_symbol: str
    provider: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    cvd_usd: float
    buy_volume_usd: float
    sell_volume_usd: float
    net_volume_usd: float
    volume_imbalance: float  # -1.0 to +1.0
    trade_count: int
    trade_intensity_per_sec: float
    
    # Large trades (> $100k notional)
    whale_buy_count: int
    whale_sell_count: int
    whale_net_usd: float
    
    # Flow Patterns
    absorption_detected: bool
    absorption_side: Optional[str] = None  # "BID_ABSORPTION" (buying limit absorbs aggressive sells) or "ASK_ABSORPTION"
    exhaustion_detected: bool
    exhaustion_side: Optional[str] = None


class OrderFlowEngineV2:
    def __init__(self, large_trade_threshold_usd: float = 100_000.0):
        self.large_trade_threshold_usd = large_trade_threshold_usd
        self._cvd_history: Dict[str, float] = {}

    def compute(self, canonical_symbol: str, provider: str, trades: List[Any], price_delta_bps: float = 0.0) -> OrderFlowFeatures:
        buy_usd = 0.0
        sell_usd = 0.0
        whale_buys = 0
        whale_sells = 0
        whale_net = 0.0

        if not trades:
            now = datetime.now(timezone.utc)
            return OrderFlowFeatures(
                canonical_symbol=canonical_symbol,
                provider=provider,
                timestamp=now,
                cvd_usd=0.0,
                buy_volume_usd=0.0,
                sell_volume_usd=0.0,
                net_volume_usd=0.0,
                volume_imbalance=0.0,
                trade_count=0,
                trade_intensity_per_sec=0.0,
                whale_buy_count=0,
                whale_sell_count=0,
                whale_net_usd=0.0,
                absorption_detected=False,
                exhaustion_detected=False
            )

        times = []
        for t in trades:
            px = getattr(t, "price", 0.0)
            sz = getattr(t, "size", 0.0)
            side = getattr(t, "side", "").lower()
            notional = px * sz
            times.append(t.event_time)

            if side == "buy":
                buy_usd += notional
                if notional >= self.large_trade_threshold_usd:
                    whale_buys += 1
                    whale_net += notional
            else:
                sell_usd += notional
                if notional >= self.large_trade_threshold_usd:
                    whale_sells += 1
                    whale_net -= notional

        net_usd = buy_usd - sell_usd
        tot_usd = buy_usd + sell_usd
        imbalance = (buy_usd - sell_usd) / tot_usd if tot_usd > 0 else 0.0

        # CVD accumulation
        key = f"{canonical_symbol}_{provider}"
        curr_cvd = self._cvd_history.get(key, 0.0) + net_usd
        self._cvd_history[key] = curr_cvd

        # Trade intensity (trades per sec over window span)
        intensity = 0.0
        if len(times) >= 2:
            span_sec = max((times[-1] - times[0]).total_seconds(), 1.0)
            intensity = len(trades) / span_sec

        # Absorption Detection:
        # High aggressive sell volume but price NOT falling (or rising) -> Bid Absorption (limit buyers absorbing sellers)
        # High aggressive buy volume but price NOT rising (or falling) -> Ask Absorption (limit sellers absorbing buyers)
        absorption = False
        absorption_side = None
        if tot_usd > 500_000.0:
            if imbalance < -0.4 and price_delta_bps >= -1.0:
                absorption = True
                absorption_side = "BID_ABSORPTION"
            elif imbalance > 0.4 and price_delta_bps <= 1.0:
                absorption = True
                absorption_side = "ASK_ABSORPTION"

        # Exhaustion Detection:
        # Price moving rapidly with low or fading aggressive volume
        exhaustion = False
        exhaustion_side = None
        if abs(price_delta_bps) > 15.0 and tot_usd < 200_000.0:
            exhaustion = True
            exhaustion_side = "UPWARD_EXHAUSTION" if price_delta_bps > 0 else "DOWNWARD_EXHAUSTION"

        return OrderFlowFeatures(
            canonical_symbol=canonical_symbol,
            provider=provider,
            cvd_usd=round(curr_cvd, 2),
            buy_volume_usd=round(buy_usd, 2),
            sell_volume_usd=round(sell_usd, 2),
            net_volume_usd=round(net_usd, 2),
            volume_imbalance=round(imbalance, 4),
            trade_count=len(trades),
            trade_intensity_per_sec=round(intensity, 2),
            whale_buy_count=whale_buys,
            whale_sell_count=whale_sells,
            whale_net_usd=round(whale_net, 2),
            absorption_detected=absorption,
            absorption_side=absorption_side,
            exhaustion_detected=exhaustion,
            exhaustion_side=exhaustion_side
        )
