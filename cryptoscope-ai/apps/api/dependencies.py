"""
CryptoScope AI - API Dependencies
Provides database sessions, verified Supabase JWT user authentication,
and Redis connection instances.
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from database.session import get_db as db_session_generator
from services.auth.supabase_verifier import supabase_verifier, SupabaseUser
from core.redis import redis_client, CanonicalRedis

security = HTTPBearer(auto_error=False)


async def get_db() -> AsyncSession:
    """Provides an active async database session."""
    async for session in db_session_generator():
        yield session


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> SupabaseUser:
    """
    Enforces verified Supabase JWT authentication.
    Extracts user_id directly from the verified cryptographic token claims.
    Rejects missing or invalid tokens with HTTP 401.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization bearer token"
        )
    try:
        user = await supabase_verifier.verify_token(credentials.credentials)
        return user
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication verification failed: {str(exc)}"
        )


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[SupabaseUser]:
    """
    Optional authentication for endpoints that support personalized responses
    when logged in, but remain publicly readable otherwise.
    """
    if not credentials:
        return None
    try:
        return await supabase_verifier.verify_token(credentials.credentials)
    except Exception:
        return None


def get_redis() -> CanonicalRedis:
    """Returns the canonical Redis singleton."""
    return redis_client
