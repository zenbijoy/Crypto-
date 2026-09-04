package com.example.core.network.client

import com.example.core.network.api.CryptoFuturesApiService
import com.example.core.network.api.CryptoScopeBackendApiService
import com.squareup.moshi.Moshi
import com.squareup.moshi.kotlin.reflect.KotlinJsonAdapterFactory
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.moshi.MoshiConverterFactory
import java.util.concurrent.TimeUnit

/**
 * Singleton network client configuring Retrofit with Moshi for both the CryptoScope AI
 * FastAPI Quant Gateway and public fallback market data services.
 */
object CryptoApiClient {

    const val LOCAL_BACKEND_URL = "http://10.0.2.2:8000/"
    const val PUBLIC_BINANCE_URL = "https://fapi.binance.com/"

    var activeBackendUrl: String = LOCAL_BACKEND_URL

    val moshi: Moshi by lazy {
        Moshi.Builder()
            .add(KotlinJsonAdapterFactory())
            .build()
    }

    private val loggingInterceptor: HttpLoggingInterceptor by lazy {
        HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BASIC
        }
    }

    val okHttpClient: OkHttpClient by lazy {
        OkHttpClient.Builder()
            .connectTimeout(10, TimeUnit.SECONDS)
            .readTimeout(10, TimeUnit.SECONDS)
            .writeTimeout(10, TimeUnit.SECONDS)
            .retryOnConnectionFailure(true)
            .addInterceptor { chain ->
                val request = chain.request().newBuilder()
                    .header("User-Agent", "CryptoScope-AI/2.4 (Android)")
                    .header("Accept", "application/json")
                    .build()
                chain.proceed(request)
            }
            .addInterceptor(loggingInterceptor)
            .build()
    }

    val retrofit: Retrofit by lazy {
        Retrofit.Builder()
            .baseUrl(PUBLIC_BINANCE_URL)
            .client(okHttpClient)
            .addConverterFactory(MoshiConverterFactory.create(moshi))
            .build()
    }

    val futuresApiService: CryptoFuturesApiService by lazy {
        retrofit.create(CryptoFuturesApiService::class.java)
    }

    val backendRetrofit: Retrofit by lazy {
        Retrofit.Builder()
            .baseUrl(activeBackendUrl)
            .client(okHttpClient)
            .addConverterFactory(MoshiConverterFactory.create(moshi))
            .build()
    }

    val backendApiService: CryptoScopeBackendApiService by lazy {
        backendRetrofit.create(CryptoScopeBackendApiService::class.java)
    }

    /**
     * Factory function to create API service with custom Base URL if needed.
     */
    fun createService(baseUrl: String = PUBLIC_BINANCE_URL): CryptoFuturesApiService {
        return Retrofit.Builder()
            .baseUrl(baseUrl)
            .client(okHttpClient)
            .addConverterFactory(MoshiConverterFactory.create(moshi))
            .build()
            .create(CryptoFuturesApiService::class.java)
    }

    fun createBackendService(baseUrl: String = LOCAL_BACKEND_URL): CryptoScopeBackendApiService {
        return Retrofit.Builder()
            .baseUrl(baseUrl)
            .client(okHttpClient)
            .addConverterFactory(MoshiConverterFactory.create(moshi))
            .build()
            .create(CryptoScopeBackendApiService::class.java)
    }
}

