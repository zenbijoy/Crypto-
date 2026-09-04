package com.example.core.network.datasource

import com.example.core.network.api.CryptoScopeBackendApiService
import com.example.core.network.client.CryptoApiClient
import com.example.core.network.dto.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

/**
 * Remote data source for CryptoScope AI FastAPI Gateway.
 * Provides fail-safe methods with real-time defaults and structured domain data.
 */
class CryptoScopeBackendRemoteDataSource(
    private val apiService: CryptoScopeBackendApiService = CryptoApiClient.backendApiService
) {

    suspend fun fetchMarketOverview(): Result<MarketOverviewResponseDto> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.getMarketOverview()
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("HTTP ${response.code()} ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun fetchFearGreed(): Result<FearGreedSummaryDto> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.getFearGreed()
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("HTTP ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun fetchEtfOverview(): Result<EtfOverviewDto> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.getEtfOverview()
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("HTTP ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun fetchRankings(type: String = "volume", limit: Int = 50): Result<List<RankingItemDto>> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.getRankings(type = type, limit = limit)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!.items)
            } else {
                Result.failure(Exception("HTTP ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun fetchScreener(): Result<ScreenerResponseDto> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.getScreener()
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("HTTP ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun fetchContractRadar(): Result<List<ContractRadarAlertDto>> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.getContractRadar()
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("HTTP ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun fetchNews(): Result<List<NewsItemDto>> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.getNews()
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("HTTP ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun fetchProvidersStatus(): Result<List<ProviderStatusDto>> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.getProvidersStatus()
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("HTTP ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
