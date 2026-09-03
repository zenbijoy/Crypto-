"""
CryptoScope AI - Order Book Microstructure Engine
Implements Section 11 specifications:
- L2 Depth calculation at 5/10/25/50 bps
- Mid price & Microprice calculation
- Multi-level Order Book Imbalance (OBI)
- Book Convexity & Liquidity Wall Detection
"""
import math
from typing import List, Dict, Tuple, Any

class OrderBookEngine:
    def __init__(self, symbol: str):
        self.symbol = symbol

    def compute_metrics(
        self,
        bids: List[Tuple[float, float]], # List of (price, size)
        asks: List[Tuple[float, float]]  # List of (price, size)
    ) -> Dict[str, Any]:
        if not bids or not asks:
            return {
                "spread_bps": 0.0,
                "mid_price": 0.0,
                "microprice": 0.0,
                "imbalance_10bps": 0.0,
                "book_convexity": 0.0,
                "liquidity_walls": []
            }

        best_bid_p, best_bid_v = bids[0]
        best_ask_p, best_ask_v = asks[0]

        mid_price = (best_bid_p + best_ask_p) / 2.0
        spread = max(0.0, best_ask_p - best_bid_p)
        spread_bps = (spread / mid_price) * 10000.0 if mid_price > 0 else 0.0

        # Microprice calculation: P_micro = (P_a * V_b + P_b * V_a) / (V_a + V_b)
        tot_top_vol = best_bid_v + best_ask_v
        if tot_top_vol > 0:
            microprice = (best_ask_p * best_bid_v + best_bid_p * best_ask_v) / tot_top_vol
        else:
            microprice = mid_price

        # Depth at 5, 10, 25, 50 bps
        depth_bps = {}
        for bps in [5, 10, 25, 50]:
            bid_cutoff = mid_price * (1.0 - bps / 10000.0)
            ask_cutoff = mid_price * (1.0 + bps / 10000.0)

            bid_vol = sum(v for p, v in bids if p >= bid_cutoff)
            ask_vol = sum(v for p, v in asks if p <= ask_cutoff)

            total_vol = bid_vol + ask_vol
            imbalance = (bid_vol - ask_vol) / total_vol if total_vol > 0 else 0.0

            depth_bps[f"bid_depth_{bps}bps"] = bid_vol
            depth_bps[f"ask_depth_{bps}bps"] = ask_vol
            depth_bps[f"imbalance_{bps}bps"] = round(imbalance, 4)

        # Detect Liquidity Walls (orders > 3x mean depth)
        avg_bid_size = sum(v for _, v in bids[:20]) / max(1, len(bids[:20]))
        avg_ask_size = sum(v for _, v in asks[:20]) / max(1, len(asks[:20]))

        walls = []
        for p, v in bids[:20]:
            if v > avg_bid_size * 2.5:
                walls.append({"side": "BID", "price": p, "volume": v, "distance_bps": round(((mid_price - p) / mid_price) * 10000, 1)})
        for p, v in asks[:20]:
            if v > avg_ask_size * 2.5:
                walls.append({"side": "ASK", "price": p, "volume": v, "distance_bps": round(((p - mid_price) / mid_price) * 10000, 1)})

        # Convexity: difference in slope between top of book and deep book
        convexity = (depth_bps.get("imbalance_50bps", 0) - depth_bps.get("imbalance_5bps", 0))

        return {
            "symbol": self.symbol,
            "mid_price": round(mid_price, 2),
            "microprice": round(microprice, 2),
            "spread_bps": round(spread_bps, 2),
            "imbalance_10bps": depth_bps.get("imbalance_10bps", 0.0),
            "depth_bps": depth_bps,
            "book_convexity": round(convexity, 4),
            "liquidity_walls": walls[:4]
        }


orderbook_engine = OrderBookEngine(symbol="BTCUSDT")

