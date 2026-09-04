# CryptoScope AI — Supabase Authentication Architecture

**Authentication Lifecycle, Server-Side Verification & Token Flow**  

---

## 1. Authentication Flow Diagram

```
[ Android Client ]
        │
        │ 1. Sign In / Sign Up (Email/Password or OAuth)
        ▼
[ Supabase Auth (GoTrue) ]
        │
        │ 2. Issues Supabase Access Token (JWT with sub, email, role)
        ▼
[ Android Client ]
        │
        │ 3. API Request with Header: "Authorization: Bearer <Supabase_JWT>"
        ▼
[ FastAPI Gateway (cryptoscope-ai/apps/api/main.py) ]
        │
        │ 4. Invokes services/auth/supabase_verifier.py
        ├── Verifies JWT signature using Supabase JWKS public keys
        ├── Verifies token expiration, issuer, and audience
        ├── Validates 'sub' UUID claim
        └── Extracts user identity (SupabaseUser)
        │
        ▼
[ Protected Route Handler ]
        │ Returns canonical response using validated user identity
```

---

## 2. Server-Side Verification Principles

1. **Zero Client Identity Trust**: FastAPI never accepts a user ID passed in request bodies or query parameters. The authenticated user ID is derived solely from the cryptographically verified `sub` claim of the Supabase JWT.
2. **Key Rotation & JWKS**: The verifier uses Supabase's standard JWKS endpoint (`/auth/v1/.well-known/jwks.json`) with in-memory caching and automatic key rotation support (RS256/ES256).
3. **Symmetric Secret Fallback**: If using HS256 tokens in local development or staging, the server verifies using `settings.SUPABASE_JWT_SECRET`.
4. **Role & Entitlement Governance**: User permissions are derived from `app_metadata` or backend user profiles. Client claims in `user_metadata` cannot elevate privileges.

---

## 3. Product Database Linkage

User profiles in the `product` schema link to Supabase via foreign identity:
```sql
CREATE TABLE product.user_profiles (
    id SERIAL PRIMARY KEY,
    supabase_user_id VARCHAR(64) UNIQUE NOT NULL,
    email VARCHAR(100) NOT NULL,
    display_name VARCHAR(100),
    avatar_url VARCHAR(255),
    preferred_currency VARCHAR(10) DEFAULT 'USD',
    theme VARCHAR(20) DEFAULT 'dark',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_user_profiles_supabase_id ON product.user_profiles(supabase_user_id);
```
No passwords or cryptographic hashes are stored in the application database.
