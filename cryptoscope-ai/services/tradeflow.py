"""
CryptoScope AI - Trade Flow & CVD Engine
Implements Section 12 specifications:
- Signed trade imbalance
- Cumulative Volume Delta (CVD)
- Aggressive flow arrival intensity
- Rolling percentile large trade identification
"""
from typing import List, Dict, Any

class TradeFlowEngine:
    def __init__(self, symbol: str):
        self.symbol = symbol

    def compute_flow_metrics(self, trades: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not trades:
            return {
                "cvd": 0.0,
                "buy_volume": 0.0,
                "sell_volume": 0.0,
                "signed_imbalance": 0.0,
                "large_trades_count": 0,
                "trade_intensity": "NORMAL"
            }

        buy_vol = sum(t["size"] for t in trades if t["side"].upper() == "BUY")
        sell_vol = sum(t["size"] for t in trades if t["side"].upper() == "SELL")
        total_vol = buy_vol + sell_vol
        cvd = buy_vol - sell_vol

        signed_imbalance = (buy_vol - sell_vol) / total_vol if total_vol > 0 else 0.0

        # Percentile-based whale trade detection
        sizes = sorted([t["size"] for t in trades])
        p95_idx = int(len(sizes) * 0.95) if len(sizes) > 0 else 0
        whale_threshold = sizes[p95_idx] if sizes else 10.0

        large_trades = [t for t in trades if t["size"] >= whale_threshold]

        intensity = "BURST" if len(trades) > 500 else ("HIGH" if len(trades) > 200 else "NORMAL")

        return {
            "symbol": self.symbol,
            "buy_volume": round(buy_vol, 2),
            "sell_volume": round(sell_vol, 2),
            "cvd": round(cvd, 2),
            "signed_imbalance": round(signed_imbalance, 4),
            "large_trades_count": len(large_trades),
            "whale_threshold": round(whale_threshold, 2),
            "trade_intensity": intensity
        }
