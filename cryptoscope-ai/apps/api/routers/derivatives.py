"""
CryptoScope AI - Canonical Derivatives Router
Handles:
- Open Interest telemetry and dispersion
- Funding rates and 8-hour rate tracking
- Funding heatmap across perpetual pairs
- Long / Short ratio analysis
"""
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from fastapi import APIRouter, Query
from services.derivatives import derivatives_engine
from services.funding_heatmap_service import funding_heatmap_service
from core.redis import redis_client

router = APIRouter(prefix="/api/v1/derivatives", tags=["Derivatives"])


def canonical_envelope(data: Any, provider: str = "AGGREGATED") -> Dict[str, Any]:
    return {
        "success": True,
        "data": data,
        "meta": {
            "source": provider,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }


@router.get("/{symbol}")
async def get_derivatives_overview(symbol: str):
    """Returns aggregated derivatives telemetry for asset (OI, Funding, Liquidations)."""
    clean_sym = symbol.upper()
    data = await derivatives_engine.get_derivatives_summary(clean_sym)
    return canonical_envelope(data)


@router.get("/funding/rates")
async def get_funding_rates(symbol: Optional[str] = Query(None)):
    """Returns funding rates across exchanges."""
    data = await derivatives_engine.get_funding_rates(symbol.upper() if symbol else "BTCUSDT")
    return canonical_envelope(data)


@router.get("/open-interest/aggregated")
async def get_aggregated_open_interest(symbol: str = Query("BTCUSDT")):
    """Returns aggregated open interest across Binance, Bybit, OKX."""
    data = await derivatives_engine.get_open_interest(symbol.upper())
    return canonical_envelope(data)


@router.get("/funding/heatmap")
async def get_funding_heatmap():
    """Returns funding rate heatmap across Tier-1/2 perpetual contracts."""
    heatmap = await funding_heatmap_service.get_heatmap()
    return canonical_envelope(heatmap)
