"""
CryptoScope AI - Watchlists & Alerts Router (Phase 18)
Protected by verified Supabase Auth JWT identity.
Endpoints:
- GET /api/v1/watchlist
- POST /api/v1/watchlist
- DELETE /api/v1/watchlist/{symbol}
- GET /api/v1/alerts
- POST /api/v1/alerts
- PATCH /api/v1/alerts/{id}
- DELETE /api/v1/alerts/{id}
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from apps.api.dependencies import get_current_user, get_db
from services.auth.supabase_verifier import SupabaseUser
from database.models import WatchlistModel, AlertRuleModel

router = APIRouter(tags=["Alerts & Watchlist"])


# ------------------ Schemas ------------------
class WatchlistAddRequest(BaseModel):
    symbol: str = Field(..., max_length=20)
    notes: Optional[str] = None


class AlertCreateRequest(BaseModel):
    symbol: str = Field(..., max_length=20)
    horizon: str = Field("1h", max_length=10)
    min_confidence: int = Field(80, ge=1, le=100)
    signal_type: str = Field("LONG", max_length=20)


class AlertUpdateRequest(BaseModel):
    is_active: Optional[bool] = None
    min_confidence: Optional[int] = Field(None, ge=1, le=100)
    signal_type: Optional[str] = None


# ------------------ Watchlist ------------------
@router.get("/api/v1/watchlist", summary="Get User Watchlist")
async def get_watchlist(
    user: SupabaseUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(WatchlistModel).where(
        (WatchlistModel.supabase_user_id == user.id)
    )
    result = await db.execute(stmt)
    items = result.scalars().all()

    formatted_items = [
        {
            "id": item.id,
            "symbol": item.symbol,
            "notes": item.notes,
            "created_at": item.created_at.isoformat() if item.created_at else None
        }
        for item in items
    ]
    return {
        "success": True,
        "data": formatted_items,
        "items": formatted_items
    }


@router.post("/api/v1/watchlist", summary="Add Symbol to Watchlist")
async def add_to_watchlist(
    req: WatchlistAddRequest,
    user: SupabaseUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    clean_sym = req.symbol.upper().replace("-", "").replace("/", "")
    # Check if already exists
    stmt = select(WatchlistModel).where(
        (WatchlistModel.supabase_user_id == user.id) & (WatchlistModel.symbol == clean_sym)
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    if existing:
        return {"success": True, "message": "Symbol already in watchlist", "data": {"id": existing.id, "symbol": clean_sym}}

    item = WatchlistModel(
        supabase_user_id=user.id,
        symbol=clean_sym,
        notes=req.notes
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return {"success": True, "data": {"id": item.id, "symbol": item.symbol}}


@router.delete("/api/v1/watchlist/{symbol}", summary="Remove Symbol from Watchlist")
async def remove_from_watchlist(
    symbol: str,
    user: SupabaseUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    clean_sym = symbol.upper().replace("-", "").replace("/", "")
    stmt = delete(WatchlistModel).where(
        (WatchlistModel.supabase_user_id == user.id) & (WatchlistModel.symbol == clean_sym)
    )
    await db.execute(stmt)
    await db.commit()
    return {"success": True, "message": f"{clean_sym} removed from watchlist"}


# ------------------ Alerts ------------------
@router.get("/api/v1/alerts", summary="Get User Alerts")
async def get_alerts(
    user: SupabaseUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(AlertRuleModel).where(
        AlertRuleModel.user_id == user.id
    )
    result = await db.execute(stmt)
    alerts = result.scalars().all()

    return {
        "success": True,
        "data": [
            {
                "id": str(a.id),
                "symbol": a.symbol,
                "horizon": a.horizon,
                "min_confidence": a.min_confidence,
                "signal_type": a.signal_type,
                "is_active": a.is_active,
                "created_at": a.created_at.isoformat() if a.created_at else None
            }
            for a in alerts
        ]
    }


@router.post("/api/v1/alerts", summary="Create New Alert")
async def create_alert(
    req: AlertCreateRequest,
    user: SupabaseUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    clean_sym = req.symbol.upper().replace("-", "").replace("/", "")
    alert = AlertRuleModel(
        user_id=user.id,
        symbol=clean_sym,
        horizon=req.horizon,
        min_confidence=req.min_confidence,
        signal_type=req.signal_type,
        is_active=True
    )
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    return {
        "success": True,
        "data": {
            "id": str(alert.id),
            "symbol": alert.symbol,
            "horizon": alert.horizon,
            "min_confidence": alert.min_confidence,
            "signal_type": alert.signal_type,
            "is_active": alert.is_active
        }
    }


@router.patch("/api/v1/alerts/{alert_id}", summary="Update Alert Status or Thresholds")
async def update_alert(
    alert_id: int,
    req: AlertUpdateRequest,
    user: SupabaseUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(AlertRuleModel).where(
        (AlertRuleModel.id == alert_id) & (AlertRuleModel.user_id == user.id)
    )
    result = await db.execute(stmt)
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    if req.is_active is not None:
        alert.is_active = req.is_active
    if req.min_confidence is not None:
        alert.min_confidence = req.min_confidence
    if req.signal_type is not None:
        alert.signal_type = req.signal_type

    await db.commit()
    await db.refresh(alert)
    return {"success": True, "data": {"id": str(alert.id), "is_active": alert.is_active}}


@router.delete("/api/v1/alerts/{alert_id}", summary="Delete Alert")
async def delete_alert(
    alert_id: int,
    user: SupabaseUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = delete(AlertRuleModel).where(
        (AlertRuleModel.id == alert_id) & (AlertRuleModel.user_id == user.id)
    )
    await db.execute(stmt)
    await db.commit()
    return {"success": True, "message": "Alert deleted"}
