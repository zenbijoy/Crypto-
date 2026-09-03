"""
CryptoScope AI - Multi-Horizon Log-Return & Triple-Barrier Labeling Engine
Implements Sections 2, 3, 4, 34:
- Target future log-returns: r_{t,h} = ln(P_{t+h} / P_t)
- Multi-horizon support: 5m, 15m, 30m, 1h, 4h, 12h, 24h
- Volatility-adjusted Triple-Barrier Labeling:
    Upper barrier: P_t * (1 + k * sigma_t) -> +1 (BULLISH)
    Lower barrier: P_t * (1 - k * sigma_t) -> -1 (BEARISH)
    Time barrier: horizon h expires without breach -> 0 (NEUTRAL / NO-SIGNAL)
"""
from typing import List, Dict, Any, Optional, Tuple
import math
from datetime import datetime, timezone

class TripleBarrierLabeler:
    def __init__(self, k_vol: float = 1.5):
        """
        :param k_vol: Multiplier for dynamic volatility threshold (k * sigma)
        """
        self.k_vol = k_vol

    def compute_log_return(self, p_current: float, p_future: float) -> float:
        """Computes r_{t,h} = ln(P_{t+h} / P_t)"""
        if p_current <= 0 or p_future <= 0:
            return 0.0
        return float(math.log(p_future / p_current))

    def price_from_log_return(self, p_current: float, log_return: float) -> float:
        """P_{t+h} = P_t * e^{r_{t,h}}"""
        return float(p_current * math.exp(log_return))

    def generate_triple_barrier_labels(
        self,
        prices: List[float],
        volatilities: List[float],
        horizon_steps: int = 12
    ) -> List[Dict[str, Any]]:
        """
        Generates purged, leakage-free triple barrier labels for historical series.
        Returns list of {
            'index': int,
            'label': int (+1, 0, -1),
            'log_return': float,
            'barrier_hit': str ('UPPER', 'LOWER', 'TIME_EXPIRY'),
            'holding_period': int
        }
        """
        n = len(prices)
        labeled_samples = []

        for t in range(n - horizon_steps):
            p0 = prices[t]
            sigma = volatilities[t] if t < len(volatilities) and volatilities[t] > 0 else 0.015
            upper_barrier = p0 * (1.0 + self.k_vol * sigma)
            lower_barrier = p0 * (1.0 - self.k_vol * sigma)

            hit_label = 0
            barrier_type = "TIME_EXPIRY"
            holding_steps = horizon_steps

            for step in range(1, horizon_steps + 1):
                p_future = prices[t + step]
                if p_future >= upper_barrier:
                    hit_label = 1
                    barrier_type = "UPPER"
                    holding_steps = step
                    break
                elif p_future <= lower_barrier:
                    hit_label = -1
                    barrier_type = "LOWER"
                    holding_steps = step
                    break

            final_p = prices[t + holding_steps]
            r_log = self.compute_log_return(p0, final_p)

            labeled_samples.append({
                "index": t,
                "label": hit_label,
                "log_return": round(r_log, 6),
                "barrier_hit": barrier_type,
                "holding_period": holding_steps,
                "p0": p0,
                "upper_barrier": round(upper_barrier, 4),
                "lower_barrier": round(lower_barrier, 4),
                "final_price": final_p
            })

        return labeled_samples

triple_barrier_labeler = TripleBarrierLabeler()
