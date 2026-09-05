package com.example.core.network.client

import com.example.BuildConfig
import com.example.core.network.api.CryptoFuturesApiService
import com.example.core.network.api.CryptoScopeBackendApiService
import com.squareup.moshi.Moshi
import com.squareup.moshi.kotlin.reflect.KotlinJsonAdapterFactory
import okhttp3.Interceptor
import okhttp3.OkHttpClient
import okhttp3.Response
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.moshi.MoshiConverterFactory
import java.util.concurrent.TimeUnit

/**
 * Institutional CryptoScope AI Network Layer (Phases 14, 15, 16)
 * - Single main backend client: [CryptoScopeApi]
 * - Configured using BuildConfig.BACKEND_BASE_URL
 * - Auth Interceptor attaches Supabase Bearer token strictly to canonical backend requests
 * - Direct exchange provider calls isolated and disabled in release builds
 */
object CryptoApiClient {

    // Canonical backend base URL configured from BuildConfig
    val BACKEND_BASE_URL: String = try {
        BuildConfig.BACKEND_BASE_URL
    } catch (e: Throwable) {
        "http://10.0.2.2:8000/"
    }

    // Direct exchange debug fallback isolated strictly to debug builds (Phase 15)
    val RAW_MARKET_DEBUG: Boolean = try {
        BuildConfig.DEBUG
    } catch (e: Throwable) {
        false
    }
    const val PUBLIC_BINANCE_URL = "https://fapi.binance.com/"

    // In-memory Supabase session token holder for Auth Interceptor (Phase 16)
    @Volatile
    var supabaseAccessToken: String? = null

    fun setAuthToken(token: String?) {
        supabaseAccessToken = token
    }

    val moshi: Moshi by lazy {
        Moshi.Builder()
            .add(KotlinJsonAdapterFactory())
            .build()
    }

    private val loggingInterceptor: HttpLoggingInterceptor by lazy {
        HttpLoggingInterceptor().apply {
            level = if (RAW_MARKET_DEBUG) HttpLoggingInterceptor.Level.BASIC else HttpLoggingInterceptor.Level.NONE
        }
    }

    /**
     * Canonical Auth Interceptor (Phase 16)
     * Attaches `Authorization: Bearer <Supabase access token>` for backend endpoints.
     * Never leaks token to external third-party or exchange providers.
     */
    private val authInterceptor = Interceptor { chain ->
        val request = chain.request()
        val requestUrl = request.url.toString()
        val builder = request.newBuilder()
            .header("User-Agent", "CryptoScope-AI/2.4 (Android)")
            .header("Accept", "application/json")

        // Only attach auth token if targeting canonical CryptoScope backend
        val token = supabaseAccessToken
        if (!token.isNullOrBlank() && requestUrl.startsWith(BACKEND_BASE_URL)) {
            builder.header("Authorization", "Bearer $token")
        }

        chain.proceed(builder.build())
    }

    val okHttpClient: OkHttpClient by lazy {
        OkHttpClient.Builder()
            .connectTimeout(15, TimeUnit.SECONDS)
            .readTimeout(15, TimeUnit.SECONDS)
            .writeTimeout(15, TimeUnit.SECONDS)
            .retryOnConnectionFailure(true)
            .addInterceptor(authInterceptor)
            .addInterceptor(loggingInterceptor)
            .build()
    }

    // Canonical Backend Retrofit Instance
    val backendRetrofit: Retrofit by lazy {
        Retrofit.Builder()
            .baseUrl(BACKEND_BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(MoshiConverterFactory.create(moshi))
            .build()
    }

    /**
     * Canonical backend service used by all production app screens
     */
    val backendApiService: CryptoScopeBackendApiService by lazy {
        backendRetrofit.create(CryptoScopeBackendApiService::class.java)
    }

    /**
     * Isolated direct provider service (disabled in production / release per Phase 15)
     */
    val futuresApiService: CryptoFuturesApiService by lazy {
        val baseUrl = if (RAW_MARKET_DEBUG) PUBLIC_BINANCE_URL else BACKEND_BASE_URL
        Retrofit.Builder()
            .baseUrl(baseUrl)
            .client(okHttpClient)
            .addConverterFactory(MoshiConverterFactory.create(moshi))
            .build()
            .create(CryptoFuturesApiService::class.java)
    }

    fun createBackendService(baseUrl: String = BACKEND_BASE_URL): CryptoScopeBackendApiService {
        return Retrofit.Builder()
            .baseUrl(baseUrl)
            .client(okHttpClient)
            .addConverterFactory(MoshiConverterFactory.create(moshi))
            .build()
            .create(CryptoScopeBackendApiService::class.java)
    }
}

/**
 * Canonical facade alias per Phase 14 specifications
 */
typealias CryptoScopeApi = CryptoScopeBackendApiService
