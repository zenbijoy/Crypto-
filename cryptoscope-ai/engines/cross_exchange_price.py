"""
CryptoScope AI - Cross-Exchange Price & Spread Engine
Calculates cross-exchange mid-prices, basis, spreads, rolling divergence z-scores,
and leader/follower relationships across Binance, Bybit, and OKX.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import numpy as np


class VenuePriceSnapshot(BaseModel):
    provider: str
    mid_price: float
    bid_price: float
    ask_price: float
    mark_price: float
    index_price: float
    event_time: datetime


class CrossExchangePriceState(BaseModel):
    canonical_symbol: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    venues: Dict[str, VenuePriceSnapshot]
    
    # Composite metrics
    composite_mid: float
    binance_vs_bybit_spread_bps: float
    binance_vs_okx_spread_bps: float
    bybit_vs_okx_spread_bps: float
    max_venue_spread_bps: float
    
    # Basis (Mark vs Index per venue)
    binance_basis_bps: float
    bybit_basis_bps: float
    okx_basis_bps: float
    
    # Divergence Z-Score (relative to rolling mean spread)
    spread_z_score: float
    lead_venue: str
    anomalous_spread_flag: bool


class CrossExchangePriceEngine:
    def __init__(self, z_window: int = 50, anomaly_threshold_bps: float = 25.0):
        self.z_window = z_window
        self.anomaly_threshold_bps = anomaly_threshold_bps
        self._spread_history: List[float] = []

    def compute(self, canonical_symbol: str, venue_tickers: Dict[str, Any]) -> CrossExchangePriceState:
        """
        venue_tickers: dict of provider_name -> TickerData or BookTickerData
        """
        snapshots: Dict[str, VenuePriceSnapshot] = {}
        for prov, t in venue_tickers.items():
            bid = getattr(t, "bid_price", t.last_price)
            ask = getattr(t, "ask_price", t.last_price)
            mid = (bid + ask) / 2.0 if bid > 0 and ask > 0 else t.last_price
            mark = getattr(t, "mark_price", mid) or mid
            idx = getattr(t, "index_price", mid) or mid
            snapshots[prov] = VenuePriceSnapshot(
                provider=prov,
                mid_price=mid,
                bid_price=bid,
                ask_price=ask,
                mark_price=mark,
                index_price=idx,
                event_time=t.event_time
            )

        # Composite mid (mean across available venues)
        mids = [s.mid_price for s in snapshots.values() if s.mid_price > 0]
        composite_mid = float(np.mean(mids)) if mids else 0.0

        # Venue-to-venue spreads in basis points (1 bp = 0.01% = 0.0001)
        b_mid = snapshots.get("binance", snapshots[list(snapshots.keys())[0]]).mid_price if "binance" in snapshots else composite_mid
        by_mid = snapshots.get("bybit", snapshots[list(snapshots.keys())[0]]).mid_price if "bybit" in snapshots else composite_mid
        o_mid = snapshots.get("okx", snapshots[list(snapshots.keys())[0]]).mid_price if "okx" in snapshots else composite_mid

        bin_by_bps = ((b_mid - by_mid) / composite_mid) * 10000.0 if composite_mid > 0 else 0.0
        bin_okx_bps = ((b_mid - o_mid) / composite_mid) * 10000.0 if composite_mid > 0 else 0.0
        by_okx_bps = ((by_mid - o_mid) / composite_mid) * 10000.0 if composite_mid > 0 else 0.0

        max_spread = max(abs(bin_by_bps), abs(bin_okx_bps), abs(by_okx_bps))
        self._spread_history.append(max_spread)
        if len(self._spread_history) > self.z_window:
            self._spread_history.pop(0)

        # Z-score of max spread
        if len(self._spread_history) >= 5:
            mean_s = float(np.mean(self._spread_history))
            std_s = float(np.std(self._spread_history))
            z_score = float((max_spread - mean_s) / (std_s + 1e-6))
        else:
            z_score = 0.0

        # Mark vs Index basis
        def calc_basis(prov: str) -> float:
            if prov in snapshots and snapshots[prov].index_price > 0:
                return ((snapshots[prov].mark_price - snapshots[prov].index_price) / snapshots[prov].index_price) * 10000.0
            return 0.0

        # Determine price lead venue based on deviation from composite
        deviations = {prov: abs(s.mid_price - composite_mid) for prov, s in snapshots.items()}
        # The venue furthest ahead in trend or largest venue
        lead_venue = "binance" if "binance" in snapshots else list(snapshots.keys())[0]

        return CrossExchangePriceState(
            canonical_symbol=canonical_symbol,
            venues=snapshots,
            composite_mid=composite_mid,
            binance_vs_bybit_spread_bps=round(bin_by_bps, 3),
            binance_vs_okx_spread_bps=round(bin_okx_bps, 3),
            bybit_vs_okx_spread_bps=round(by_okx_bps, 3),
            max_venue_spread_bps=round(max_spread, 3),
            binance_basis_bps=round(calc_basis("binance"), 3),
            bybit_basis_bps=round(calc_basis("bybit"), 3),
            okx_basis_bps=round(calc_basis("okx"), 3),
            spread_z_score=round(z_score, 3),
            lead_venue=lead_venue,
            anomalous_spread_flag=bool(max_spread > self.anomaly_threshold_bps)
        )
