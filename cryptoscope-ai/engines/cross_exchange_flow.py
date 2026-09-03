"""
CryptoScope AI - Cross-Exchange Flow Aggregator
Aggregates trade flow, CVD, and volume imbalances across venues to identify
broad-market institutional accumulation or distribution.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from engines.order_flow_v2 import OrderFlowFeatures


class CrossExchangeFlowState(BaseModel):
    canonical_symbol: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    aggregate_cvd_usd: float
    aggregate_buy_usd: float
    aggregate_sell_usd: float
    aggregate_net_usd: float
    global_volume_imbalance: float
    
    venue_cvd: Dict[str, float]
    venue_imbalances: Dict[str, float]
    
    flow_alignment_score: float  # 1.0 (all 3 buy), -1.0 (all 3 sell), ~0 (conflicted)
    institutional_aggression_bias: str  # STRONG_BUY_AGGRESSION, MODERATE_BUY, BALANCED, MODERATE_SELL, STRONG_SELL_AGGRESSION


class CrossExchangeFlowAggregator:
    def compute(self, canonical_symbol: str, venue_flows: Dict[str, OrderFlowFeatures]) -> CrossExchangeFlowState:
        tot_buy = sum(f.buy_volume_usd for f in venue_flows.values())
        tot_sell = sum(f.sell_volume_usd for f in venue_flows.values())
        tot_net = tot_buy - tot_sell
        tot_vol = tot_buy + tot_sell
        global_imb = tot_net / tot_vol if tot_vol > 0 else 0.0

        v_cvd = {p: f.cvd_usd for p, f in venue_flows.items()}
        v_imb = {p: f.volume_imbalance for p, f in venue_flows.items()}

        # Flow alignment
        imb_signs = [1 if imb > 0.05 else (-1 if imb < -0.05 else 0) for imb in v_imb.values()]
        alignment = sum(imb_signs) / max(len(imb_signs), 1)

        # Institutional aggression classification
        if global_imb > 0.35 and alignment >= 0.6:
            bias = "STRONG_BUY_AGGRESSION"
        elif global_imb > 0.1:
            bias = "MODERATE_BUY"
        elif global_imb < -0.35 and alignment <= -0.6:
            bias = "STRONG_SELL_AGGRESSION"
        elif global_imb < -0.1:
            bias = "MODERATE_SELL"
        else:
            bias = "BALANCED"

        return CrossExchangeFlowState(
            canonical_symbol=canonical_symbol,
            aggregate_cvd_usd=round(sum(v_cvd.values()), 2),
            aggregate_buy_usd=round(tot_buy, 2),
            aggregate_sell_usd=round(tot_sell, 2),
            aggregate_net_usd=round(tot_net, 2),
            global_volume_imbalance=round(global_imb, 4),
            venue_cvd=v_cvd,
            venue_imbalances=v_imb,
            flow_alignment_score=round(alignment, 2),
            institutional_aggression_bias=bias
        )
