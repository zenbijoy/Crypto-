# CryptoScope AI — Android Backend Integration Specification

**Mobile Network Architecture, Auth Interceptor, Offline Caching & Invariant Rules**  

---

## 1. Zero Direct Exchange Calls Policy

In production runtime mode:
- **Android client NEVER directly calls Binance, Bybit, OKX, or paid provider endpoints.**
- All market telemetry, klines, orderbooks, open interest, liquidations, predictions, and health queries pass through the CryptoScope FastAPI gateway (`CryptoScopeBackendApiService`).
- Raw exchange connections (`CryptoFuturesApiService`) are isolated as offline dev fallbacks and disabled in production builds.

---

## 2. Network Client Architecture

```
[ Android UI Layer (Compose Screens) ]
        │
        ▼
[ CryptoViewModel ]
        │
        ▼
[ CryptoScopeRepository ]
        │
        ├──> [ Room Database (CryptoScopeDatabase) ] (Local Offline Cache)
        │
        └──> [ CryptoScopeBackendRemoteDataSource ]
                 │
                 ▼
             [ OkHttpClient with AuthInterceptor ]
                 │ Attaches: "Authorization: Bearer <Supabase_JWT>"
                 │ Timeout: 15s connect, 30s read
                 │ Retries with exponential backoff on 5xx
                 ▼
             [ Retrofit Service: CryptoScopeBackendApiService ]
                 │ Path: /api/v1/...
                 ▼
             [ FastAPI Backend Gateway ]
```

---

## 3. UI State Lifecycle Protocol

Every Jetpack Compose view model models state via a strict sealed class hierarchy, eliminating false financial placeholders:

```kotlin
sealed interface UiState<out T> {
    object Loading : UiState<Nothing>
    data class Live<T>(val data: T, val lastUpdated: Long) : UiState<T>
    data class Cached<T>(val data: T, val cacheAgeSeconds: Long) : UiState<T>
    data class Stale<T>(val data: T, val warning: String) : UiState<T>
    data class Unavailable(val reason: String) : UiState<Nothing>
    data class Error(val message: String, val canRetry: Boolean) : UiState<Nothing>
    object Unauthenticated : UiState<Nothing>
}
```

- While network requests are in flight, UI displays a shimmer / skeleton placeholder.
- If offline, Room database provides cached data with a visible "Offline Cached" chip.
- Never show hardcoded "$67,500" or fake profit values while loading.
