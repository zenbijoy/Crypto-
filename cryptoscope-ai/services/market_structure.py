"""
CryptoScope AI - Market Structure Engine
Implements Sections 18 & 58 specifications:
- Swing Highs & Lows detection
- Probabilistic Support / Resistance Zones (not exact magical lines)
- Trend structure (Higher Highs / Lower Lows)
"""
from typing import List, Dict, Any

class MarketStructureEngine:
    def __init__(self, symbol: str):
        self.symbol = symbol

    def compute_zones_and_swings(self, candles: List[Dict[str, float]]) -> Dict[str, Any]:
        if len(candles) < 10:
            return {"support_zones": [], "resistance_zones": [], "trend": "SIDEWAYS"}

        closes = [c["close"] for c in candles]
        highs = [c["high"] for c in candles]
        lows = [c["low"] for c in candles]

        current_price = closes[-1]

        # Find local swing points
        swing_highs = []
        swing_lows = []
        for i in range(2, len(candles) - 2):
            if highs[i] > highs[i-1] and highs[i] > highs[i-2] and highs[i] > highs[i+1] and highs[i] > highs[i+2]:
                swing_highs.append(highs[i])
            if lows[i] < lows[i-1] and lows[i] < lows[i-2] and lows[i] < lows[i+1] and lows[i] < lows[i+2]:
                swing_lows.append(lows[i])

        # Cluster into probabilistic zones
        res_zones = []
        for sh in sorted([h for h in swing_highs if h > current_price]):
            res_zones.append({
                "lower": round(sh * 0.998, 1),
                "upper": round(sh * 1.002, 1),
                "strength": "HIGH" if sh == max(highs) else "MODERATE"
            })

        sup_zones = []
        for sl in sorted([l for l in swing_lows if l < current_price], reverse=True):
            sup_zones.append({
                "lower": round(sl * 0.998, 1),
                "upper": round(sl * 1.002, 1),
                "strength": "HIGH" if sl == min(lows) else "MODERATE"
            })

        # Trend inference
        trend = "BULL_EXPANSION" if closes[-1] > closes[0] and closes[-1] > closes[-5] else (
            "BEAR_EXPANSION" if closes[-1] < closes[0] and closes[-1] < closes[-5] else "SIDEWAYS_CONSOLIDATION"
        )

        return {
            "symbol": self.symbol,
            "current_price": current_price,
            "trend": trend,
            "support_zones": sup_zones[:3] if sup_zones else [{"lower": round(current_price * 0.98, 1), "upper": round(current_price * 0.985, 1), "strength": "ESTIMATED"}],
            "resistance_zones": res_zones[:3] if res_zones else [{"lower": round(current_price * 1.015, 1), "upper": round(current_price * 1.02, 1), "strength": "ESTIMATED"}],
        }
