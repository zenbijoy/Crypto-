"""
CryptoScope AI - Canonical Order Book Router
Handles:
- L2 depth snapshots (bids & asks)
- Bid/ask spread in bps
- Order book depth imbalance
- Multi-exchange aggregated order book
"""
from datetime import datetime, timezone
from typing import Dict, Any
from fastapi import APIRouter, Query
from services.orderbook import orderbook_engine
from services.aggregated_orderbook_service import aggregated_orderbook_service

router = APIRouter(prefix="/api/v1/orderbook", tags=["Orderbook"])


@router.get("/{symbol}")
@router.get("")
async def get_orderbook(symbol: str = Query("BTCUSDT"), depth: int = Query(50)):
    """Returns orderbook depth and microstructure imbalance metrics."""
    data = await orderbook_engine.get_depth(symbol.upper(), depth=depth)
    return {
        "success": True,
        "symbol": symbol.upper(),
        "depth": depth,
        "data": data,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/aggregated/{symbol}")
async def get_aggregated_orderbook(symbol: str = "BTCUSDT"):
    """Returns multi-exchange orderbook depth from Binance, Bybit, and OKX."""
    data = await aggregated_orderbook_service.get_aggregated_depth(symbol.upper())
    return {
        "success": True,
        "symbol": symbol.upper(),
        "data": data,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
