package com.example.core.network.datasource

import com.example.core.network.api.ExchangePriceApiService
import com.example.core.network.client.CryptoApiClient
import com.example.core.network.dto.ExchangeTickerDto
import com.example.core.network.dto.OrderBookResponseDto
import com.example.core.network.dto.DerivativesSummaryResponseDto
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

/**
 * Remote data source for fetching real-time crypto price data from the
 * configured exchange endpoints via Retrofit.
 */
class ExchangePriceRemoteDataSource(
    private val apiService: ExchangePriceApiService = CryptoApiClient.exchangePriceApiService
) {

    /**
     * Fetches real-time ticker price for a specific symbol (e.g. "BTCUSDT").
     */
    suspend fun fetchRealTimePrice(symbol: String): Result<ExchangeTickerDto> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.getRealTimeTicker(symbol)
            if (response.isSuccessful && response.body()?.data != null) {
                Result.success(response.body()!!.data!!)
            } else {
                Result.failure(Exception("Failed to fetch price for $symbol: HTTP ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Fetches summarized real-time tickers for all active pairs.
     */
    suspend fun fetchMarketsSummary(): Result<List<ExchangeTickerDto>> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.getMarketsSummary()
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!.data)
            } else {
                Result.failure(Exception("Failed to fetch markets summary: HTTP ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Fetches real-time order book depth for a symbol.
     */
    suspend fun fetchOrderBook(symbol: String, depth: Int = 50): Result<OrderBookResponseDto> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.getOrderBook(symbol, depth)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Failed to fetch order book for $symbol: HTTP ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Fetches aggregated order book across exchanges for a symbol.
     */
    suspend fun fetchAggregatedOrderBook(symbol: String): Result<OrderBookResponseDto> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.getAggregatedOrderBook(symbol)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Failed to fetch aggregated order book for $symbol: HTTP ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Fetches real-time derivatives overview (OI, funding rate, liquidation stats).
     */
    suspend fun fetchDerivativesOverview(symbol: String): Result<DerivativesSummaryResponseDto> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.getDerivativesOverview(symbol)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Failed to fetch derivatives overview for $symbol: HTTP ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
