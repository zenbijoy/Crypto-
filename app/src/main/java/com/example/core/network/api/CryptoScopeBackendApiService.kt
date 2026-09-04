package com.example.core.network.api

import com.example.core.network.dto.*
import retrofit2.Response
import retrofit2.http.GET
import retrofit2.http.Path
import retrofit2.http.Query

/**
 * Retrofit interface for the institutional CryptoScope AI Gateway (/api/v1/...)
 */
interface CryptoScopeBackendApiService {

    @GET("api/v1/market/overview")
    suspend fun getMarketOverview(): Response<MarketOverviewResponseDto>

    @GET("api/v1/sentiment/fear-greed")
    suspend fun getFearGreed(): Response<FearGreedSummaryDto>

    @GET("api/v1/etf/overview")
    suspend fun getEtfOverview(): Response<EtfOverviewDto>

    @GET("api/v1/rankings")
    suspend fun getRankings(
        @Query("type") type: String = "volume",
        @Query("market") market: String = "perpetual",
        @Query("limit") limit: Int = 50
    ): Response<RankingsResponseDto>

    @GET("api/v1/screener")
    suspend fun getScreener(
        @Query("sort_by") sortBy: String = "volume_24h_usd",
        @Query("limit") limit: Int = 50
    ): Response<ScreenerResponseDto>

    @GET("api/v1/radar/contracts")
    suspend fun getContractRadar(): Response<List<ContractRadarAlertDto>>

    @GET("api/v1/predictions/{symbol}")
    suspend fun getPrediction(
        @Path("symbol") symbol: String,
        @Query("horizon") horizon: String = "15m"
    ): Response<AiPredictionDto>

    @GET("api/v1/news")
    suspend fun getNews(
        @Query("category") category: String = "All",
        @Query("limit") limit: Int = 20
    ): Response<List<NewsItemDto>>

    @GET("api/v1/events")
    suspend fun getEvents(): Response<List<MarketEventItemDto>>

    @GET("api/v1/providers/status")
    suspend fun getProvidersStatus(): Response<List<ProviderStatusDto>>
}
