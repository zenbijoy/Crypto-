package com.example.core.network.api

import com.example.core.network.dto.*
import retrofit2.Response
import retrofit2.http.GET
import retrofit2.http.Query

/**
 * Retrofit interface for public Crypto Futures exchange REST API.
 * Uses Binance Futures public API endpoints (zero API key required for public market data).
 */
interface CryptoFuturesApiService {

    /**
     * Fetch 24hr ticker price change statistics for all symbols or a single symbol.
     */
    @GET("fapi/v1/ticker/24hr")
    suspend fun get24HrTickers(): Response<List<Futures24HrTickerDto>>

    @GET("fapi/v1/ticker/24hr")
    suspend fun get24HrTicker(
        @Query("symbol") symbol: String
    ): Response<Futures24HrTickerDto>

    /**
     * Fetch mark price, index price and latest funding rate.
     */
    @GET("fapi/v1/premiumIndex")
    suspend fun getPremiumIndex(
        @Query("symbol") symbol: String? = null
    ): Response<List<FuturesPremiumIndexDto>>

    @GET("fapi/v1/premiumIndex")
    suspend fun getSinglePremiumIndex(
        @Query("symbol") symbol: String
    ): Response<FuturesPremiumIndexDto>

    /**
     * Fetch current open interest for a specific futures contract.
     */
    @GET("fapi/v1/openInterest")
    suspend fun getOpenInterest(
        @Query("symbol") symbol: String
    ): Response<FuturesOpenInterestDto>

    /**
     * Fetch L2 order book depth bids and asks.
     * Limit can be 5, 10, 20, 50, 100, 500, 1000.
     */
    @GET("fapi/v1/depth")
    suspend fun getOrderBookDepth(
        @Query("symbol") symbol: String,
        @Query("limit") limit: Int = 20
    ): Response<FuturesOrderBookDto>

    /**
     * Fetch candlestick (kline) historical bars.
     */
    @GET("fapi/v1/klines")
    suspend fun getKlines(
        @Query("symbol") symbol: String,
        @Query("interval") interval: String = "1h",
        @Query("limit") limit: Int = 50
    ): Response<List<List<Any>>>

    /**
     * Fetch top trader long/short account ratio.
     */
    @GET("futures/data/topLongShortPositionRatio")
    suspend fun getTopLongShortRatio(
        @Query("symbol") symbol: String,
        @Query("period") period: String = "1h",
        @Query("limit") limit: Int = 10
    ): Response<List<FuturesLongShortRatioDto>>

    /**
     * Fetch exchange metadata and active trading pairs.
     */
    @GET("fapi/v1/exchangeInfo")
    suspend fun getExchangeInfo(): Response<FuturesExchangeInfoDto>
}
