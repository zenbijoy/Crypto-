# CryptoScope AI — Security Architecture & Threat Model

**Defense-in-Depth, Secret Hygiene, JWT Validation & Zero-Trust Policies**  

---

## 1. Perimeter & Edge Defense (Cloudflare)

1. **DDoS & Web Application Firewall (WAF)**: Cloudflare inspects incoming HTTP requests, mitigating volumetric DDoS attacks and blocking malicious SQLi/XSS patterns before traffic reaches the origin.
2. **Strict TLS 1.3**: Encryption in transit is enforced from mobile client through Cloudflare to FastAPI.
3. **Private Subnet Isolation**: PostgreSQL, TimescaleDB, and Redis clusters are bound to private VPC subnets with zero public ingress.

---

## 2. Token Security & Cryptographic Verifications

1. **Server-Side Token Verification**: FastAPI validates Supabase JWT signatures, expiration (`exp`), issuer (`iss`), and audience (`aud`).
2. **Zero Client Trust**: All mutations, watchlist additions, alert creation, and profile updates use the user UUID verified from the JWT.
3. **Admin Role Isolation**: Admin endpoints (`/api/v1/admin/*`) require explicit `admin` role verified server-side from `app_metadata` or the backend user profile. Client-submitted roles are rejected.

---

## 3. Secret Management & Zero-Leakage Invariants

1. **No Committed Secrets**: The repository contains zero production API keys, Supabase service role keys, Firebase private keys, or database passwords. All configuration is injected via environment variables.
2. **Android App Hardening**: No sensitive backend database or cloud provider keys are embedded in APK builds. The Android app receives only public anon keys for Supabase Auth and talks to the authenticated backend.
3. **CORS Security**: Cross-Origin Resource Sharing is locked to explicit trusted domains (`settings.CORS_ORIGINS`). Wildcards (`"*"`) with `allow_credentials=True` are strictly prohibited.
4. **Structured JSON Logs**: Sensitive user data (passwords, raw tokens, credit details) is redacted from logging pipelines.
