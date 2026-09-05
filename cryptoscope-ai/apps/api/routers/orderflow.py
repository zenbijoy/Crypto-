"""
CryptoScope AI - Canonical Order Flow Router
Handles:
- Cumulative Volume Delta (CVD)
- Aggressive buy/sell imbalances
- Whale trade radar & large flow detections
"""
from datetime import datetime, timezone
from typing import Dict, Any
from fastapi import APIRouter, Query
from services.tradeflow import tradeflow_engine

router = APIRouter(prefix="/api/v1/orderflow", tags=["Orderflow"])


@router.get("/{symbol}")
async def get_orderflow(symbol: str = "BTCUSDT", limit: int = Query(100)):
    """Returns CVD, aggressive trade flow, and delta metrics for asset."""
    data = await tradeflow_engine.get_trade_flow_summary(symbol.upper(), limit=limit)
    return {
        "success": True,
        "symbol": symbol.upper(),
        "data": data,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/cvd/{symbol}")
async def get_cvd_series(symbol: str = "BTCUSDT", timeframe: str = Query("1h")):
    """Returns time-series cumulative volume delta."""
    data = await tradeflow_engine.get_cvd_series(symbol.upper(), timeframe=timeframe)
    return {
        "success": True,
        "symbol": symbol.upper(),
        "timeframe": timeframe,
        "series": data,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
