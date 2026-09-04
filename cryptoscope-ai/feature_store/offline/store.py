"""
Offline Feature Store computing features identical to Online Store formulas.
Phase 9: Offline Feature Store.
"""
from __future__ import annotations
import math
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import polars as pl

from feature_store.definitions.core import CORE_FEATURE_SPECS


class OfflineFeatureStore:
    """Computes exact offline feature representations sharing core definitions to prevent train/serve skew."""

    @staticmethod
    def compute_orderbook_features(
        best_bid: float,
        best_ask: float,
        bid_vol_10bps: float,
        ask_vol_10bps: float
    ) -> Dict[str, float]:
        mid = (best_bid + best_ask) / 2.0
        spread_bps = ((best_ask - best_bid) / mid * 10000.0) if mid > 0 else 0.0
        tot_vol = bid_vol_10bps + ask_vol_10bps
        microprice = ((ask_vol_10bps * best_bid + bid_vol_10bps * best_ask) / tot_vol) if tot_vol > 0 else mid
        order_imbalance = ((bid_vol_10bps - ask_vol_10bps) / tot_vol) if tot_vol > 0 else 0.0
        return {
            "spread_bps": round(spread_bps, 4),
            "microprice": round(microprice, 4),
            "order_imbalance": round(order_imbalance, 4)
        }

    @staticmethod
    def compute_trade_features(
        prices: List[float],
        taker_buys: List[float],
        taker_sells: List[float]
    ) -> Dict[str, float]:
        if len(prices) < 2:
            return {"realized_volatility_5m": 0.0, "cvd_quote": 0.0}

        log_returns = [math.log(prices[i] / prices[i - 1]) for i in range(1, len(prices)) if prices[i - 1] > 0]
        if not log_returns:
            vol = 0.0
        else:
            mean_ret = sum(log_returns) / len(log_returns)
            variance = sum((r - mean_ret) ** 2 for r in log_returns) / max(1, len(log_returns) - 1)
            vol = math.sqrt(variance) * math.sqrt(300) * 100.0

        cvd = sum(taker_buys) - sum(taker_sells)
        return {
            "realized_volatility_5m": round(vol, 4),
            "cvd_quote": round(cvd, 2)
        }

    @staticmethod
    def compute_derivatives_features(
        funding_rate: float,
        mark_price: float,
        index_price: float,
        long_liq_usd: float = 0.0,
        short_liq_usd: float = 0.0
    ) -> Dict[str, float]:
        basis = ((mark_price - index_price) / index_price * (365 * 24 / 8) * 100.0) if index_price > 0 else 0.0
        liq_intensity = (long_liq_usd - short_liq_usd) / 1_000_000.0
        return {
            "funding_rate": round(funding_rate, 6),
            "basis_annualized": round(basis, 4),
            "liquidation_intensity": round(liq_intensity, 4)
        }

    @classmethod
    def compute_offline_vector(
        cls,
        best_bid: float,
        best_ask: float,
        bid_vol_10bps: float,
        ask_vol_10bps: float,
        prices: List[float],
        taker_buys: List[float],
        taker_sells: List[float],
        funding_rate: float,
        mark_price: float,
        index_price: float,
        long_liq_usd: float = 0.0,
        short_liq_usd: float = 0.0
    ) -> Dict[str, float]:
        """Compute complete offline feature vector for research & model training."""
        f_ob = cls.compute_orderbook_features(best_bid, best_ask, bid_vol_10bps, ask_vol_10bps)
        f_tr = cls.compute_trade_features(prices, taker_buys, taker_sells)
        f_drv = cls.compute_derivatives_features(funding_rate, mark_price, index_price, long_liq_usd, short_liq_usd)

        return {**f_ob, **f_tr, **f_drv}


offline_feature_store = OfflineFeatureStore()
