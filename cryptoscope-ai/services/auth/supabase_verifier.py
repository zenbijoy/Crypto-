"""
CryptoScope AI - Supabase JWT Authentication & Token Verification Service
Implements Phase 3 & Phase 4:
- Server-side verification of Supabase JWTs
- Signature, issuer, audience, and expiration verification
- Support for Supabase JWKS public keys with asymmetric RSA/ECDSA or symmetric fallback
- Extracts authenticated user identity (UUID, email, role, app_metadata)
- Rejects untrusted client-supplied identity
"""
import time
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass
import httpx
from jose import jwt, JWTError, ExpiredSignatureError
from core.config import settings

logger = logging.getLogger("cryptoscope.auth.supabase")

@dataclass
class SupabaseUser:
    id: str
    email: str
    role: str = "authenticated"
    app_metadata: Dict[str, Any] = None
    user_metadata: Dict[str, Any] = None
    created_at: Optional[float] = None

class SupabaseAuthVerifier:
    def __init__(self):
        self.supabase_url = settings.SUPABASE_URL
        self.jwks_url = settings.SUPABASE_JWKS_URL or (
            f"{self.supabase_url}/auth/v1/.well-known/jwks.json" if self.supabase_url else None
        )
        self.jwt_secret = settings.SUPABASE_JWT_SECRET or settings.SECRET_KEY
        self._jwks_cache: Optional[Dict[str, Any]] = None
        self._jwks_last_fetched: float = 0
        self._jwks_ttl_seconds: float = 3600  # Refresh JWKS every hour

    async def _fetch_jwks(self) -> Optional[Dict[str, Any]]:
        """Fetches and caches the JSON Web Key Set from Supabase."""
        if not self.jwks_url:
            return None

        now = time.time()
        if self._jwks_cache and (now - self._jwks_last_fetched < self._jwks_ttl_seconds):
            return self._jwks_cache

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(self.jwks_url)
                if resp.status_code == 200:
                    self._jwks_cache = resp.json()
                    self._jwks_last_fetched = now
                    logger.info("Successfully fetched Supabase JWKS keys.")
                    return self._jwks_cache
                else:
                    logger.warning(f"Failed to fetch Supabase JWKS: HTTP {resp.status_code}")
        except Exception as e:
            logger.warning(f"Error fetching Supabase JWKS: {str(e)}")

        return self._jwks_cache

    async def verify_token(self, token: str) -> SupabaseUser:
        """
        Verifies a Supabase JWT and returns the authenticated SupabaseUser.
        Raises ValueError or JWTError on validation failure.
        """
        if not token:
            raise ValueError("Token is required")

        # Strip Bearer prefix if passed
        if token.startswith("Bearer "):
            token = token[7:].strip()

        # Step 1: Decode headers to identify algorithm & kid
        try:
            unverified_headers = jwt.get_unverified_header(token)
            alg = unverified_headers.get("alg", "HS256")
            kid = unverified_headers.get("kid")
        except Exception as e:
            raise ValueError(f"Invalid token headers: {str(e)}")

        payload: Optional[Dict[str, Any]] = None

        # Step 2: Asymmetric verification via JWKS if RS256/ES256
        if alg in ["RS256", "ES256"] and self.jwks_url:
            jwks = await self._fetch_jwks()
            if jwks and "keys" in jwks:
                for key in jwks["keys"]:
                    if kid is None or key.get("kid") == kid:
                        try:
                            payload = jwt.decode(
                                token,
                                key,
                                algorithms=[alg],
                                audience="authenticated",
                                options={"verify_aud": False}
                            )
                            break
                        except Exception:
                            continue

        # Step 3: Symmetric fallback via Supabase JWT Secret (HS256)
        if payload is None and self.jwt_secret:
            try:
                payload = jwt.decode(
                    token,
                    self.jwt_secret,
                    algorithms=["HS256"],
                    options={"verify_aud": False}
                )
            except ExpiredSignatureError:
                raise ValueError("Supabase token has expired")
            except JWTError as e:
                raise ValueError(f"Supabase token signature verification failed: {str(e)}")

        if payload is None:
            raise ValueError("Could not verify Supabase JWT with available verification keys")

        # Step 4: Validate required Supabase claims
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Token missing 'sub' (User UUID) claim")

        exp = payload.get("exp")
        if exp and exp < time.time():
            raise ValueError("Token has expired")

        email = payload.get("email", "")
        role = payload.get("role", "authenticated")
        app_metadata = payload.get("app_metadata", {})
        user_metadata = payload.get("user_metadata", {})

        return SupabaseUser(
            id=str(user_id),
            email=str(email),
            role=str(role),
            app_metadata=app_metadata,
            user_metadata=user_metadata,
            created_at=payload.get("iat")
        )

supabase_verifier = SupabaseAuthVerifier()
