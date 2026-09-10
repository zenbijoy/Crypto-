"""
CryptoScope AI - Virtual Paper Trading Router (Phases 2 & 18)
Protected by verified Supabase Auth JWT identity.
Simulates realistic order execution with slippage, taker fees, liquidation prices, and PnL.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid

from apps.api.dependencies import get_current_user, get_db
from services.auth.supabase_verifier import SupabaseUser
from services.paper_trading import PaperTradingEngine
from services.aggregation import market_aggregator
from database.session import AsyncSession

router = APIRouter(prefix="/api/v1/paper", tags=["Paper Trading"])
paper_engine = PaperTradingEngine()


class PaperOrderRequest(BaseModel):
    symbol: str = Field(..., max_length=20)
    side: str = Field(...)
    size_usd: float = Field(..., gt=0)
    leverage: float = Field(2.0, ge=1.0, le=50.0)


@router.get("/positions", summary="Get Active Paper Positions")
async def get_paper_positions(user: SupabaseUser = Depends(get_current_user)):
    """Returns active paper positions for the authenticated user."""
    acct = paper_engine.get_account(user.id)
    positions_list = list(acct.positions.values())
    return {
        "success": True,
        "data": {
            "account_equity_usd": round(acct.equity_usd, 2),
            "available_balance_usd": round(acct.available_balance_usd, 2),
            "realized_pnl_usd": round(acct.realized_pnl_usd, 2),
            "positions": [p.dict() if hasattr(p, "dict") else p for p in positions_list]
        }
    }


@router.post("/order", summary="Submit Paper Execution Order")
async def submit_paper_order(
    req: PaperOrderRequest,
    user: SupabaseUser = Depends(get_current_user)
):
    clean_sym = req.symbol.upper().replace("-", "").replace("/", "")
    base = clean_sym.replace("USDT", "").replace("USDC", "").replace("USD", "")
    
    # Get truthful live mid price
    current_mid = None
    try:
        mkt = await market_aggregator.aggregate_asset_market_data(base)
        current_mid = mkt.get("price")
        if not current_mid and isinstance(mkt.get("consensus_price"), dict):
            current_mid = mkt["consensus_price"].get("value")
    except Exception:
        pass

    if not current_mid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Live market price unavailable for {clean_sym}; order rejected."
        )

    normalized_side = "BUY" if req.side.upper() in ["BUY", "LONG"] else "SELL"
    try:
        execution = paper_engine.execute_market_order(
            symbol=clean_sym,
            side=normalized_side,
            size_usd=req.size_usd,
            current_mid=current_mid,
            spread_bps=1.5,
            leverage=req.leverage,
            user_id=user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return {"success": True, "data": execution}


@router.post("/positions/{pos_id}/close", summary="Close Active Paper Position")
async def close_paper_position(
    pos_id: str,
    user: SupabaseUser = Depends(get_current_user)
):
    acct = paper_engine.get_account(user.id)
    pos = acct.positions.get(pos_id)
    if not pos:
        # Check by symbol
        pos = next((p for p in acct.positions.values() if p.symbol == pos_id), None)
    
    if not pos:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Position {pos_id} not found")

    base = pos.symbol.replace("USDT", "").replace("USDC", "").replace("USD", "")
    current_mid = None
    try:
        mkt = await market_aggregator.aggregate_asset_market_data(base)
        current_mid = mkt.get("price")
        if not current_mid and isinstance(mkt.get("consensus_price"), dict):
            current_mid = mkt["consensus_price"].get("value")
    except Exception:
        pass

    if not current_mid:
        current_mid = pos.entry_price

    res = paper_engine.close_position(pos.position_id, current_mid=current_mid, user_id=user.id)
    return {"success": True, "message": f"Position {pos_id} closed", "data": res}
