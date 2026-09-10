package com.example.core.network.api

import com.example.core.network.dto.CanonicalMarketSummaryResponseDto
import com.example.core.network.dto.CanonicalMarketTickerResponseDto
import com.example.core.network.dto.DerivativesSummaryResponseDto
import com.example.core.network.dto.OrderBookResponseDto
import retrofit2.Response
import retrofit2.http.GET
import retrofit2.http.Path
import retrofit2.http.Query

/**
 * Retrofit service definition for fetching real-time cryptocurrency market
 * prices and derivatives metrics from the configured institutional exchange gateway.
 */
interface ExchangePriceApiService {

    /**
     * Fetch real-time ticker price for a specific trading pair (e.g. "BTCUSDT").
     * Uses the canonical markets endpoint configured to poll multi-exchange providers.
     */
    @GET("api/v1/markets/{symbol}")
    suspend fun getRealTimeTicker(
        @Path("symbol") symbol: String
    ): Response<CanonicalMarketTickerResponseDto>

    /**
     * Fetch real-time tickers for all active pairs across supported exchanges.
     */
    @GET("api/v1/markets/summary")
    suspend fun getMarketsSummary(): Response<CanonicalMarketSummaryResponseDto>

    /**
     * Fetch real-time order book depth for a specific trading pair.
     */
    @GET("api/v1/orderbook/{symbol}")
    suspend fun getOrderBook(
        @Path("symbol") symbol: String,
        @Query("depth") depth: Int = 50
    ): Response<OrderBookResponseDto>

    /**
     * Fetch multi-exchange aggregated order book depth (Binance, Bybit, OKX).
     */
    @GET("api/v1/orderbook/aggregated/{symbol}")
    suspend fun getAggregatedOrderBook(
        @Path("symbol") symbol: String
    ): Response<OrderBookResponseDto>

    /**
     * Fetch real-time derivatives metrics (Open Interest, Funding Rate, Liquidations).
     */
    @GET("api/v1/derivatives/{symbol}")
    suspend fun getDerivativesOverview(
        @Path("symbol") symbol: String
    ): Response<DerivativesSummaryResponseDto>

    /**
     * Fetch real-time funding rates across exchanges.
     */
    @GET("api/v1/derivatives/funding/rates")
    suspend fun getFundingRates(
        @Query("symbol") symbol: String? = null
    ): Response<DerivativesSummaryResponseDto>
}
