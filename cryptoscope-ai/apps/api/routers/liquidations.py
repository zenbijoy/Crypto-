"""
CryptoScope AI - Canonical Liquidations Router
Handles:
- Real-time liquidation events and aggregated pools
- Liquidation heatmap and cascade levels
"""
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from fastapi import APIRouter, Query
from services.liquidation_analytics_service import liquidation_analytics_service

router = APIRouter(prefix="/api/v1/liquidations", tags=["Liquidations"])


@router.get("/{symbol}")
async def get_liquidations(symbol: str = "BTCUSDT", limit: int = Query(50)):
    """Returns recent liquidation events and 24h total liquidations."""
    data = await liquidation_analytics_service.get_liquidations(symbol.upper(), limit=limit)
    return {
        "success": True,
        "symbol": symbol.upper(),
        "data": data,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/heatmap/{symbol}")
async def get_liquidation_heatmap(symbol: str = "BTCUSDT"):
    """Returns estimated liquidation levels and leverage clustering."""
    data = await liquidation_analytics_service.get_liquidation_heatmap(symbol.upper())
    return {
        "success": True,
        "symbol": symbol.upper(),
        "levels": data,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
