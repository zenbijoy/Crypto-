"""
Shared Feature Definitions and Metadata Specification.
Phase 8, 9, 10: Feature Store Definitions.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional


@dataclass(frozen=True)
class FeatureSpec:
    name: str
    version: str
    formula: str
    dependencies: List[str]
    window_seconds: int
    source: str
    availability_rule: str
    max_freshness_seconds: float
    description: str


# Standard shared feature catalog
CORE_FEATURE_SPECS: Dict[str, FeatureSpec] = {
    "spread_bps": FeatureSpec(
        name="spread_bps",
        version="v2.0",
        formula="(ask_price - bid_price) / mid_price * 10000",
        dependencies=["market:orderbook"],
        window_seconds=0,
        source="orderbook",
        availability_rule="mandatory",
        max_freshness_seconds=5.0,
        description="Top of book relative spread in basis points"
    ),
    "microprice": FeatureSpec(
        name="microprice",
        version="v2.0",
        formula="(ask_vol * bid_price + bid_vol * ask_price) / (bid_vol + ask_vol)",
        dependencies=["market:orderbook"],
        window_seconds=0,
        source="orderbook",
        availability_rule="mandatory",
        max_freshness_seconds=5.0,
        description="Volume-weighted microprice indicator"
    ),
    "order_imbalance": FeatureSpec(
        name="order_imbalance",
        version="v2.0",
        formula="(bid_vol_10bps - ask_vol_10bps) / (bid_vol_10bps + ask_vol_10bps)",
        dependencies=["market:orderbook"],
        window_seconds=0,
        source="orderbook",
        availability_rule="mandatory",
        max_freshness_seconds=5.0,
        description="Normalized orderbook volume imbalance within 10 bps"
    ),
    "realized_volatility_5m": FeatureSpec(
        name="realized_volatility_5m",
        version="v2.0",
        formula="std(log_returns_1s) * sqrt(300) * 100",
        dependencies=["market:trades"],
        window_seconds=300,
        source="trades",
        availability_rule="mandatory",
        max_freshness_seconds=15.0,
        description="5-minute annualized high-frequency realized volatility"
    ),
    "cvd_quote": FeatureSpec(
        name="cvd_quote",
        version="v2.0",
        formula="sum(taker_buy_quote) - sum(taker_sell_quote)",
        dependencies=["market:trades"],
        window_seconds=300,
        source="trades",
        availability_rule="mandatory",
        max_freshness_seconds=15.0,
        description="Cumulative volume delta in quote currency over 5m window"
    ),
    "funding_rate": FeatureSpec(
        name="funding_rate",
        version="v2.0",
        formula="last_funding_rate",
        dependencies=["market:funding"],
        window_seconds=28800,
        source="funding",
        availability_rule="mandatory",
        max_freshness_seconds=300.0,
        description="Latest 8-hour perpetual funding rate"
    ),
    "basis_annualized": FeatureSpec(
        name="basis_annualized",
        version="v2.0",
        formula="(mark_price - index_price) / index_price * (365 * 24 / 8) * 100",
        dependencies=["market:funding"],
        window_seconds=300,
        source="derivatives",
        availability_rule="optional",
        max_freshness_seconds=60.0,
        description="Annualized perpetual basis premium in percent"
    ),
    "liquidation_intensity": FeatureSpec(
        name="liquidation_intensity",
        version="v2.0",
        formula="(long_liq_usd - short_liq_usd) / 1000000.0",
        dependencies=["market:liquidations"],
        window_seconds=900,
        source="liquidations",
        availability_rule="optional",
        max_freshness_seconds=120.0,
        description="Net 15m liquidation imbalance intensity in millions USD"
    ),
}
