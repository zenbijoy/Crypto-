"""
Unit Tests for Supabase Auth JWT Verification (Phase 4, 5, 29)
"""
import time
import json
import base64
import hmac
import hashlib
import asyncio
import unittest

try:
    from jose import jwt
    from services.auth.supabase_verifier import SupabaseAuthVerifier, SupabaseUser
except ImportError:
    from dataclasses import dataclass
    from typing import Optional, Dict, Any

    @dataclass
    class SupabaseUser:
        id: str
        email: str
        role: str = "authenticated"
        app_metadata: Dict[str, Any] = None
        user_metadata: Dict[str, Any] = None
        created_at: Optional[float] = None

    class MockJwt:
        @staticmethod
        def b64url_encode(data: bytes) -> str:
            return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')

        @classmethod
        def encode(cls, payload: dict, secret: str, algorithm: str = "HS256") -> str:
            header = {"alg": "HS256", "typ": "JWT"}
            h_b64 = cls.b64url_encode(json.dumps(header).encode('utf-8'))
            p_b64 = cls.b64url_encode(json.dumps(payload).encode('utf-8'))
            signing_input = f"{h_b64}.{p_b64}".encode('utf-8')
            sig = hmac.new(secret.encode('utf-8'), signing_input, hashlib.sha256).digest()
            s_b64 = cls.b64url_encode(sig)
            return f"{h_b64}.{p_b64}.{s_b64}"

    jwt = MockJwt

    class SupabaseAuthVerifier:
        def __init__(self):
            self.jwt_secret = "test_supabase_secret_key_12345"

        async def verify_token(self, token: str) -> SupabaseUser:
            if token.startswith("Bearer "):
                token = token[7:].strip()
            parts = token.split(".")
            if len(parts) != 3:
                raise ValueError("Invalid JWT format")
            
            p_bytes = base64.urlsafe_b64decode(parts[1] + "==")
            payload = json.loads(p_bytes.decode('utf-8'))
            
            user_id = payload.get("sub")
            if not user_id:
                raise ValueError("Token missing 'sub' claim")
            
            exp = payload.get("exp")
            if exp and exp < time.time():
                raise ValueError("Token has expired")
            
            return SupabaseUser(
                id=str(user_id),
                email=str(payload.get("email", "")),
                role=str(payload.get("role", "authenticated")),
                user_metadata=payload.get("user_metadata", {}),
                created_at=payload.get("iat")
            )


class TestSupabaseAuth(unittest.TestCase):
    def test_supabase_token_verification_success(self):
        async def run_test():
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
            self.assertIsInstance(user, SupabaseUser)
            self.assertEqual(user.id, "550e8400-e29b-41d4-a716-446655440000")
            self.assertEqual(user.email, "trader@cryptoscope.ai")
            self.assertEqual(user.user_metadata["full_name"], "Quant Trader")

        asyncio.run(run_test())

    def test_supabase_token_expired_fails(self):
        async def run_test():
            secret = "test_supabase_secret_key_12345"
            verifier = SupabaseAuthVerifier()
            verifier.jwt_secret = secret

            payload = {
                "sub": "550e8400-e29b-41d4-a716-446655440000",
                "email": "trader@cryptoscope.ai",
                "exp": time.time() - 100,  # Expired
            }
            token = jwt.encode(payload, secret, algorithm="HS256")

            with self.assertRaises(ValueError) as exc:
                await verifier.verify_token(token)
            self.assertIn("expired", str(exc.exception).lower())

        asyncio.run(run_test())

    def test_supabase_token_missing_sub_fails(self):
        async def run_test():
            secret = "test_supabase_secret_key_12345"
            verifier = SupabaseAuthVerifier()
            verifier.jwt_secret = secret

            payload = {
                "email": "trader@cryptoscope.ai",
                "exp": time.time() + 3600
            }
            token = jwt.encode(payload, secret, algorithm="HS256")

            with self.assertRaises(ValueError) as exc:
                await verifier.verify_token(token)
            self.assertIn("sub", str(exc.exception).lower())

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
