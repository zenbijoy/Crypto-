"""
CryptoScope AI - Authentication Router (Phase 4 & 5)
Supabase Auth is the single identity source.
Backend verifies Supabase JWT via signature/JWKS/claims.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from apps.api.dependencies import get_current_user, get_optional_user
from services.auth.supabase_verifier import SupabaseUser
from core.config import settings

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.get("/verify", summary="Verify Supabase JWT Session")
async def verify_auth_token(user: SupabaseUser = Depends(get_current_user)):
    """
    Validates client's Bearer token issued by Supabase Auth.
    Returns authenticated user information.
    """
    return {
        "success": True,
        "data": {
            "authenticated": True,
            "user_id": user.id,
            "email": user.email,
            "role": user.role,
            "app_metadata": user.app_metadata,
            "user_metadata": user.user_metadata
        }
    }


@router.get("/config", summary="Supabase Client Auth Config")
async def get_auth_config():
    """
    Returns public Supabase endpoint and anonymous key for mobile client initialization.
    Does NOT leak backend secrets.
    """
    return {
        "success": True,
        "data": {
            "supabase_url": settings.SUPABASE_URL or "",
            "supabase_anon_key": settings.SUPABASE_ANON_KEY or "",
            "auth_provider": "supabase"
        }
    }
