"""
Online vs. Offline Feature Parity Validator.
Phase 9: Training-Serving Skew Prevention.
"""
from __future__ import annotations
import math
from datetime import datetime, timezone
from typing import Any, Dict, Tuple

from feature_store.offline.store import offline_feature_store
from feature_store.online.store import online_feature_store


class FeatureParityValidator:
    """Verifies that online computed features match offline computed features within strict floating point tolerances."""

    @staticmethod
    async def verify_parity(
        symbol: str,
        horizon: str,
        best_bid: float,
        best_ask: float,
        bid_vol_10bps: float,
        ask_vol_10bps: float,
        prices: list[float],
        taker_buys: list[float],
        taker_sells: list[float],
        funding_rate: float,
        mark_price: float,
        index_price: float,
        tolerance: float = 1e-4
    ) -> Dict[str, Any]:
        # 1. Compute offline vector
        offline_vec = offline_feature_store.compute_offline_vector(
            best_bid=best_bid,
            best_ask=best_ask,
            bid_vol_10bps=bid_vol_10bps,
            ask_vol_10bps=ask_vol_10bps,
            prices=prices,
            taker_buys=taker_buys,
            taker_sells=taker_sells,
            funding_rate=funding_rate,
            mark_price=mark_price,
            index_price=index_price
        )

        # 2. Ingest same vector into online store
        now = datetime.now(timezone.utc)
        await online_feature_store.put_feature_vector(
            symbol=symbol,
            horizon=horizon,
            feature_values=offline_vec,
            event_time=now,
            feature_version="v2.0"
        )

        # 3. Read back from online store
        online_vec, avail_mask, _ = await online_feature_store.get_feature_vector(
            symbol=symbol,
            horizon=horizon,
            feature_version="v2.0"
        )

        # 4. Compare every feature
        mismatches = []
        for fname, off_val in offline_vec.items():
            on_val = online_vec.get(fname)
            if on_val is None or math.isnan(on_val):
                mismatches.append({"feature": fname, "reason": "Missing in online store"})
                continue
            diff = abs(on_val - off_val)
            if diff > tolerance:
                mismatches.append({
                    "feature": fname,
                    "offline": off_val,
                    "online": on_val,
                    "delta": diff
                })

        parity_passed = len(mismatches) == 0
        return {
            "parity_passed": parity_passed,
            "compared_features_count": len(offline_vec),
            "mismatches": mismatches,
            "offline_sample": offline_vec,
            "online_sample": {k: online_vec[k] for k in offline_vec if k in online_vec}
        }


feature_parity_validator = FeatureParityValidator()
