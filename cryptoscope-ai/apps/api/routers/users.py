"""
CryptoScope AI - User Product Profile Router (Phases 6 & 18)
Protected by verified Supabase Auth JWT identity.
Interacts with product.user_profiles in PostgreSQL.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from apps.api.dependencies import get_current_user, get_db
from services.auth.supabase_verifier import SupabaseUser
from database.models import UserProfileModel, DeviceTokenModel

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


class UserProfileUpdateRequest(BaseModel):
    display_name: Optional[str] = Field(None, max_length=100)
    avatar_url: Optional[str] = Field(None, max_length=255)
    timezone: Optional[str] = Field(None, max_length=50)
    preferred_currency: Optional[str] = Field(None, max_length=10)
    default_asset: Optional[str] = Field(None, max_length=20)
    default_horizon: Optional[str] = Field(None, max_length=10)
    theme: Optional[str] = Field(None, max_length=20)
    language: Optional[str] = Field(None, max_length=10)


class DeviceRegistrationRequest(BaseModel):
    device_token: str = Field(..., max_length=255)
    platform: str = Field("android", max_length=20)


@router.get("/me", summary="Get Authenticated User Product Profile")
async def get_my_profile(
    user: SupabaseUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves the verified user's product profile from PostgreSQL.
    If the profile does not exist yet, creates initial record populated from Supabase JWT claims.
    """
    stmt = select(UserProfileModel).where(UserProfileModel.user_id == user.id)
    result = await db.execute(stmt)
    profile = result.scalar_one_or_none()

    if not profile:
        profile = UserProfileModel(
            user_id=user.id,
            supabase_user_id=user.id,
            email=user.email,
            display_name=user.user_metadata.get("full_name") or user.email.split("@")[0],
            avatar_url=user.user_metadata.get("avatar_url"),
            timezone="UTC",
            preferred_currency="USD",
            default_asset="BTC",
            default_horizon="1h",
            theme="dark",
            language="en"
        )
        db.add(profile)
        await db.commit()
        await db.refresh(profile)

    return {
        "success": True,
        "data": {
            "user_id": profile.user_id,
            "email": profile.email,
            "display_name": profile.display_name,
            "avatar_url": profile.avatar_url,
            "timezone": profile.timezone,
            "preferred_currency": profile.preferred_currency,
            "default_asset": profile.default_asset,
            "default_horizon": profile.default_horizon,
            "theme": profile.theme,
            "language": profile.language,
            "created_at": profile.created_at.isoformat() if profile.created_at else None,
            "updated_at": profile.updated_at.isoformat() if profile.updated_at else None
        }
    }


@router.patch("/me", summary="Update User Product Profile")
async def update_my_profile(
    req: UserProfileUpdateRequest,
    user: SupabaseUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Updates the authenticated user's profile settings in the database.
    Does NOT allow updating user_id (immutable Supabase identity).
    """
    stmt = select(UserProfileModel).where(UserProfileModel.user_id == user.id)
    result = await db.execute(stmt)
    profile = result.scalar_one_or_none()

    if not profile:
        profile = UserProfileModel(
            user_id=user.id,
            supabase_user_id=user.id,
            email=user.email,
            timezone="UTC",
            preferred_currency="USD",
            default_asset="BTC",
            default_horizon="1h",
            theme="dark",
            language="en"
        )
        db.add(profile)

    if req.display_name is not None:
        profile.display_name = req.display_name
    if req.avatar_url is not None:
        profile.avatar_url = req.avatar_url
    if req.timezone is not None:
        profile.timezone = req.timezone
    if req.preferred_currency is not None:
        profile.preferred_currency = req.preferred_currency
    if req.default_asset is not None:
        profile.default_asset = req.default_asset.upper()
    if req.default_horizon is not None:
        profile.default_horizon = req.default_horizon
    if req.theme is not None:
        profile.theme = req.theme
    if req.language is not None:
        profile.language = req.language

    profile.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(profile)

    return {
        "success": True,
        "data": {
            "user_id": profile.user_id,
            "display_name": profile.display_name,
            "avatar_url": profile.avatar_url,
            "timezone": profile.timezone,
            "preferred_currency": profile.preferred_currency,
            "default_asset": profile.default_asset,
            "default_horizon": profile.default_horizon,
            "theme": profile.theme,
            "language": profile.language,
            "updated_at": profile.updated_at.isoformat()
        }
    }


@router.post("/devices", summary="Register Mobile Device Token for Push Notifications")
async def register_device(
    req: DeviceRegistrationRequest,
    user: SupabaseUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Registers an FCM or APNS device push token under the authenticated user."""
    stmt = select(DeviceTokenModel).where(DeviceTokenModel.device_token == req.device_token)
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing:
        existing.supabase_user_id = user.id
        existing.enabled = True
        existing.last_seen = datetime.now(timezone.utc)
    else:
        new_token = DeviceTokenModel(
            supabase_user_id=user.id,
            device_token=req.device_token,
            platform=req.platform,
            enabled=True
        )
        db.add(new_token)

    await db.commit()
    return {"success": True, "message": "Device token registered successfully."}
