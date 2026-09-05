# Android Network Layer Forensic Audit

**Document Version**: 2.0  
**Status**: Consolidating to Single Canonical Client  
**Directive**: Inventory all network clients in the Android codebase. Remove direct exchange couplings and enforce `CryptoScopeApi` as the sole network entry point.

---

## 1. Client Inventory

| Client / Service Interface | Target Base URL | Authentication | Status | Migration Action |
|:---|:---|:---|:---|:---|
| `CryptoScopeBackendApiService` | `BuildConfig.BACKEND_BASE_URL` (`/api/v1`) | Supabase JWT (`Bearer <token>`) via Auth Interceptor | **CANONICAL** | Primary client for all product screens. |
| `CryptoFuturesApiService` | Direct Binance (`https://fapi.binance.com/`) | None (Public REST) | **LEGACY / DEBUG ONLY** | Isolated behind `RAW_MARKET_DEBUG` build flag. Disabled in production release builds. |
| `CryptoApiClient` | Unified OkHttpClient & Retrofit factory | Injected Supabase JWT interceptor | **CANONICAL** | Manages timeouts, retry policies, and session token injection. |

---

## 2. Direct Provider Audit (Binance, Bybit, Coinglass, Alternative.me, CryptoPanic)

1. **Binance Futures REST (`fapi.binance.com`)**:
   - Previously called directly by `CryptoFuturesApiService`.
   - **Remediation**: All market data (tickers, candles, orderbook, trades, funding, open interest, and liquidations) is now ingested by the canonical backend (`cryptoscope-ai`) and served through `/api/v1/markets/*`, `/api/v1/candles/*`, `/api/v1/derivatives/*`, and `/api/v1/orderbook/*`.
   - In production builds (`!RAW_MARKET_DEBUG`), direct exchange calls are prohibited.

2. **Bybit & OKX**:
   - No direct network calls exist in Android app.
   - External provider connectivity is strictly owned by backend.

3. **Alternative.me (Fear & Greed Index)**:
   - Handled exclusively via backend `/api/v1/sentiment/fear-greed`.

4. **Farside Investors (ETF Flow)**:
   - Handled exclusively via backend `/api/v1/etf/overview`.

5. **CryptoPanic (News)**:
   - Handled exclusively via backend `/api/v1/news`.

---

## 3. Auth Interceptor Verification

- Token injected dynamically: `CryptoApiClient.setAuthToken(supabaseToken)`.
- Attached strictly to requests matching `BACKEND_BASE_URL`.
- Headers attached:
  - `Authorization: Bearer <Supabase access token>`
  - `User-Agent: CryptoScope-AI/2.4 (Android)`
  - `Accept: application/json`
- Zero token leakage to external third-party or debug endpoints.
