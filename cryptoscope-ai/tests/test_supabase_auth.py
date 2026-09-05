"""
Unit Tests for Supabase Auth JWT Verification (Phase 4, 5, 29)
"""
import time
import pytest
from jose import jwt
from services.auth.supabase_verifier import SupabaseAuthVerifier, SupabaseUser


@pytest.mark.asyncio
async def test_supabase_token_verification_success():
    secret = "test_supabase_secret_key_12345"
    verifier = SupabaseAuthVerifier()
    verifier.jwt_secret = secret

    payload = {
        "sub": "550e8400-e29b-41d4-a716-446655440000",
        "email": "trader@cryptoscope.ai",
        "role": "authenticated",
        "exp": time.time() + 3600,
        "iat": time.time(),
        "user_metadata": {"full_name": "Quant Trader"}
    }
    token = jwt.encode(payload, secret, algorithm="HS256")

    user = await verifier.verify_token(f"Bearer {token}")
    assert isinstance(user, SupabaseUser)
    assert user.id == "550e8400-e29b-41d4-a716-446655440000"
    assert user.email == "trader@cryptoscope.ai"
    assert user.user_metadata["full_name"] == "Quant Trader"


@pytest.mark.asyncio
async def test_supabase_token_expired_fails():
    secret = "test_supabase_secret_key_12345"
    verifier = SupabaseAuthVerifier()
    verifier.jwt_secret = secret

    payload = {
        "sub": "550e8400-e29b-41d4-a716-446655440000",
        "email": "trader@cryptoscope.ai",
        "exp": time.time() - 100,  # Expired
    }
    token = jwt.encode(payload, secret, algorithm="HS256")

    with pytest.raises(ValueError) as exc:
        await verifier.verify_token(token)
    assert "expired" in str(exc.value).lower()


@pytest.mark.asyncio
async def test_supabase_token_missing_sub_fails():
    secret = "test_supabase_secret_key_12345"
    verifier = SupabaseAuthVerifier()
    verifier.jwt_secret = secret

    payload = {
        "email": "trader@cryptoscope.ai",
        "exp": time.time() + 3600
    }
    token = jwt.encode(payload, secret, algorithm="HS256")

    with pytest.raises(ValueError) as exc:
        await verifier.verify_token(token)
    assert "sub" in str(exc.value).lower()
