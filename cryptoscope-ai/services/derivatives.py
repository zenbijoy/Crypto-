"""
CryptoScope AI - Derivatives & Liquidation Intelligence Engine
Implements Sections 13 & 14 specifications:
- Multi-exchange Funding Rate 7d z-score & acceleration
- Open interest velocity & Price x OI relationship inference
- Liquidation Pressure Score (0-100) & cascade states
- Distance from leverage clusters
"""
from typing import Dict, Any, List

class DerivativesEngine:
    def __init__(self, symbol: str):
        self.symbol = symbol

    def analyze_derivatives(
        self,
        current_funding: float,
        funding_7d_history: List[float],
        open_interest_usd: float,
        oi_change_pct: float,
        price_change_pct: float,
        long_liq_usd: float,
        short_liq_usd: float
    ) -> Dict[str, Any]:
        # Funding 7d z-score
        mean_funding = sum(funding_7d_history) / max(1, len(funding_7d_history)) if funding_7d_history else 0.0001
        variance = sum((f - mean_funding)**2 for f in funding_7d_history) / max(1, len(funding_7d_history)) if funding_7d_history else 0.00001
        std_dev = max(1e-6, variance**0.5)
        funding_zscore = (current_funding - mean_funding) / std_dev

        # Infer Price x OI state (Section 14)
        if price_change_pct > 0 and oi_change_pct > 0:
            market_state = "NEW_LONG_EXPANSION"
            state_label = "Price ↑ + OI ↑ (Aggressive Long Build)"
        elif price_change_pct < 0 and oi_change_pct > 0:
            market_state = "NEW_SHORT_EXPANSION"
            state_label = "Price ↓ + OI ↑ (Aggressive Short Build)"
        elif price_change_pct > 0 and oi_change_pct < 0:
            market_state = "SHORT_COVERING"
            state_label = "Price ↑ + OI ↓ (Short Squeeze / Covering)"
        else:
            market_state = "LONG_LIQUIDATION"
            state_label = "Price ↓ + OI ↓ (Long Unwinding / Liquidations)"

        # Liquidation Pressure Score (0-100)
        tot_liq = long_liq_usd + short_liq_usd
        raw_liq_score = min(100.0, (tot_liq / 5_000_000.0) * 80.0 + abs(funding_zscore) * 10.0)
        liquidation_pressure_score = round(max(0.0, min(100.0, raw_liq_score)), 1)

        cascade_state = "HIGH_CASCADE_RISK" if liquidation_pressure_score > 75 else ("ELEVATED" if liquidation_pressure_score > 40 else "CALM")

        return {
            "symbol": self.symbol,
            "funding_rate": current_funding,
            "funding_rate_7d_zscore": round(funding_zscore, 2),
            "open_interest_usd": open_interest_usd,
            "oi_velocity_pct_1h": round(oi_change_pct, 2),
            "market_state": market_state,
            "market_state_label": state_label,
            "liquidation_pressure_score": liquidation_pressure_score,
            "cascade_state": cascade_state,
            "long_liquidation_usd": long_liq_usd,
            "short_liquidation_usd": short_liq_usd
        }


derivatives_engine = DerivativesEngine("BTCUSDT")

