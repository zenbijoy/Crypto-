"""
CryptoScope AI - Advanced Order Book Features Engine
Calculates microprice, multi-level depth at 5/10/25/50/100 bps,
order book slope, multi-level OBI, queue imbalance, and price impact for standard notional sizes.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import numpy as np


class OrderBookFeatures(BaseModel):
    canonical_symbol: str
    provider: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    bid_price: float
    ask_price: float
    mid_price: float
    spread: float
    spread_bps: float
    microprice: float
    microprice_divergence_bps: float  # (microprice - mid) / mid * 10000
    
    # Depths at BPS thresholds (Cumulative USD)
    bid_depth_5bps_usd: float
    ask_depth_5bps_usd: float
    bid_depth_10bps_usd: float
    ask_depth_10bps_usd: float
    bid_depth_25bps_usd: float
    ask_depth_25bps_usd: float
    bid_depth_50bps_usd: float
    ask_depth_50bps_usd: float
    bid_depth_100bps_usd: float
    ask_depth_100bps_usd: float
    
    # Multi-level OBI: (Bid - Ask) / (Bid + Ask)
    obi_level_1: float
    obi_level_5: float
    obi_level_10: float
    obi_level_20: float
    
    # Book Slope (liquidity accumulation rate)
    bid_slope: float
    ask_slope: float
    slope_asymmetry: float  # bid_slope - ask_slope
    
    # Price Impact Estimates (basis points slippage for market orders)
    impact_100k_usd_bps: float
    impact_500k_usd_bps: float
    impact_1m_usd_bps: float


class OrderBookFeatureEngine:
    def compute(self, canonical_symbol: str, provider: str, bids: List[List[float]], asks: List[List[float]]) -> OrderBookFeatures:
        """
        bids: [[price, size], ...] sorted descending
        asks: [[price, size], ...] sorted ascending
        """
        if not bids or not asks:
            now = datetime.now(timezone.utc)
            return OrderBookFeatures(
                canonical_symbol=canonical_symbol,
                provider=provider,
                timestamp=now,
                bid_price=0.0,
                ask_price=0.0,
                mid_price=0.0,
                spread=0.0,
                spread_bps=0.0,
                microprice=0.0,
                microprice_divergence_bps=0.0,
                bid_depth_5bps_usd=0.0, ask_depth_5bps_usd=0.0,
                bid_depth_10bps_usd=0.0, ask_depth_10bps_usd=0.0,
                bid_depth_25bps_usd=0.0, ask_depth_25bps_usd=0.0,
                bid_depth_50bps_usd=0.0, ask_depth_50bps_usd=0.0,
                bid_depth_100bps_usd=0.0, ask_depth_100bps_usd=0.0,
                obi_level_1=0.0, obi_level_5=0.0, obi_level_10=0.0, obi_level_20=0.0,
                bid_slope=0.0, ask_slope=0.0, slope_asymmetry=0.0,
                impact_100k_usd_bps=0.0, impact_500k_usd_bps=0.0, impact_1m_usd_bps=0.0
            )

        best_bid = float(bids[0][0])
        best_bid_sz = float(bids[0][1])
        best_ask = float(asks[0][0])
        best_ask_sz = float(asks[0][1])

        mid = (best_bid + best_ask) / 2.0
        spread = best_ask - best_bid
        spread_bps = (spread / mid) * 10000.0 if mid > 0 else 0.0

        # Microprice: (Q_b * P_a + Q_a * P_b) / (Q_b + Q_a)
        tot_top_sz = best_bid_sz + best_ask_sz
        if tot_top_sz > 0:
            microprice = (best_bid_sz * best_ask + best_ask_sz * best_bid) / tot_top_sz
            micro_div_bps = ((microprice - mid) / mid) * 10000.0
        else:
            microprice = mid
            micro_div_bps = 0.0

        # Depth at BPS bands
        bps_tiers = [5, 10, 25, 50, 100]
        bid_depths = {b: 0.0 for b in bps_tiers}
        ask_depths = {b: 0.0 for b in bps_tiers}

        for p, s in bids:
            price_dist_bps = ((mid - p) / mid) * 10000.0
            usd_val = p * s
            for b in bps_tiers:
                if price_dist_bps <= b:
                    bid_depths[b] += usd_val

        for p, s in asks:
            price_dist_bps = ((p - mid) / mid) * 10000.0
            usd_val = p * s
            for b in bps_tiers:
                if price_dist_bps <= b:
                    ask_depths[b] += usd_val

        # Multi-level OBI
        def calc_obi(depth_n: int) -> float:
            b_sub = sum(p * s for p, s in bids[:depth_n])
            a_sub = sum(p * s for p, s in asks[:depth_n])
            tot = b_sub + a_sub
            return (b_sub - a_sub) / tot if tot > 0 else 0.0

        obi_1 = calc_obi(1)
        obi_5 = calc_obi(5)
        obi_10 = calc_obi(10)
        obi_20 = calc_obi(20)

        # Book Slope: regression of cumulative volume vs distance from mid
        bid_dists = [abs(mid - p) for p, s in bids[:20]]
        bid_cum_vols = np.cumsum([p * s for p, s in bids[:20]])
        ask_dists = [abs(p - mid) for p, s in asks[:20]]
        ask_cum_vols = np.cumsum([p * s for p, s in asks[:20]])

        b_slope = float(np.polyfit(bid_dists, bid_cum_vols, 1)[0]) if len(bid_dists) > 2 and np.std(bid_dists) > 0 else 0.0
        a_slope = float(np.polyfit(ask_dists, ask_cum_vols, 1)[0]) if len(ask_dists) > 2 and np.std(ask_dists) > 0 else 0.0

        # Price impact estimates for $100k, $500k, $1M buy orders (asks traversal)
        def calc_impact(target_usd: float) -> float:
            accum_usd = 0.0
            cost_weighted_px = 0.0
            for p, s in asks:
                chunk_usd = p * s
                remaining_usd = target_usd - accum_usd
                if chunk_usd >= remaining_usd:
                    cost_weighted_px += p * remaining_usd
                    accum_usd += remaining_usd
                    break
                else:
                    cost_weighted_px += p * chunk_usd
                    accum_usd += chunk_usd
            if accum_usd >= target_usd and target_usd > 0:
                avg_exec_px = cost_weighted_px / target_usd
                return ((avg_exec_px - mid) / mid) * 10000.0
            return 999.0  # Void / not enough depth

        return OrderBookFeatures(
            canonical_symbol=canonical_symbol,
            provider=provider,
            bid_price=best_bid,
            ask_price=best_ask,
            mid_price=round(mid, 3),
            spread=round(spread, 3),
            spread_bps=round(spread_bps, 3),
            microprice=round(microprice, 3),
            microprice_divergence_bps=round(micro_div_bps, 3),
            bid_depth_5bps_usd=round(bid_depths[5], 2),
            ask_depth_5bps_usd=round(ask_depths[5], 2),
            bid_depth_10bps_usd=round(bid_depths[10], 2),
            ask_depth_10bps_usd=round(ask_depths[10], 2),
            bid_depth_25bps_usd=round(bid_depths[25], 2),
            ask_depth_25bps_usd=round(ask_depths[25], 2),
            bid_depth_50bps_usd=round(bid_depths[50], 2),
            ask_depth_50bps_usd=round(ask_depths[50], 2),
            bid_depth_100bps_usd=round(bid_depths[100], 2),
            ask_depth_100bps_usd=round(ask_depths[100], 2),
            obi_level_1=round(obi_1, 4),
            obi_level_5=round(obi_5, 4),
            obi_level_10=round(obi_10, 4),
            obi_level_20=round(obi_20, 4),
            bid_slope=round(b_slope, 2),
            ask_slope=round(a_slope, 2),
            slope_asymmetry=round(b_slope - a_slope, 2),
            impact_100k_usd_bps=round(calc_impact(100_000.0), 3),
            impact_500k_usd_bps=round(calc_impact(500_000.0), 3),
            impact_1m_usd_bps=round(calc_impact(1_000_000.0), 3)
        )
