package com.example.core.network.datasource

import com.example.core.model.*
import com.example.core.network.api.CryptoFuturesApiService
import com.example.core.network.client.CryptoApiClient
import com.example.core.network.dto.Futures24HrTickerDto
import com.example.core.network.dto.FuturesOrderBookDto
import com.example.core.network.dto.FuturesPremiumIndexDto
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

/**
 * Remote data source for fetching public cryptocurrency futures data via Retrofit.
 */
class FuturesRemoteDataSource(
    private val apiService: CryptoFuturesApiService = CryptoApiClient.futuresApiService
) {

    /**
     * Fetches 24hr tickers for active futures pairs and maps them to domain MarketItem objects.
     */
    suspend fun fetch24HrTickers(): Result<List<Futures24HrTickerDto>> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.get24HrTickers()
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Failed to fetch 24hr tickers: HTTP ${response.code()} ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Fetches single 24hr ticker for a given symbol (e.g. "BTCUSDT").
     */
    suspend fun fetchTicker(symbol: String): Result<Futures24HrTickerDto> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.get24HrTicker(symbol)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Failed to fetch ticker for $symbol: HTTP ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Fetches funding rate and premium index data.
     */
    suspend fun fetchPremiumIndex(symbol: String? = null): Result<List<FuturesPremiumIndexDto>> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.getPremiumIndex(symbol)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Failed to fetch premium index: HTTP ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Fetches live open interest in USD/contracts for a symbol.
     */
    suspend fun fetchOpenInterest(symbol: String): Result<Double> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.getOpenInterest(symbol)
            if (response.isSuccessful && response.body() != null) {
                val oi = response.body()!!.openInterest?.toDoubleOrNull() ?: 0.0
                Result.success(oi)
            } else {
                Result.failure(Exception("Failed to fetch open interest for $symbol: HTTP ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Fetches L2 order book depth and converts to domain OrderBookData.
     */
    suspend fun fetchOrderBook(symbol: String, limit: Int = 20): Result<OrderBookData> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.getOrderBookDepth(symbol, limit)
            if (response.isSuccessful && response.body() != null) {
                val dto = response.body()!!
                val bids = mutableListOf<OrderBookEntry>()
                var cumBid = 0.0
                dto.bids.take(8).forEach { entry ->
                    val price = entry.getOrNull(0)?.toDoubleOrNull() ?: 0.0
                    val amount = entry.getOrNull(1)?.toDoubleOrNull() ?: 0.0
                    cumBid += amount
                    bids.add(OrderBookEntry(price, amount, Math.round(cumBid * 1000.0) / 1000.0))
                }

                val asks = mutableListOf<OrderBookEntry>()
                var cumAsk = 0.0
                dto.asks.take(8).forEach { entry ->
                    val price = entry.getOrNull(0)?.toDoubleOrNull() ?: 0.0
                    val amount = entry.getOrNull(1)?.toDoubleOrNull() ?: 0.0
                    cumAsk += amount
                    asks.add(OrderBookEntry(price, amount, Math.round(cumAsk * 1000.0) / 1000.0))
                }

                val bestBid = bids.firstOrNull()?.price ?: 0.0
                val bestAsk = asks.firstOrNull()?.price ?: 0.0
                val midPrice = if (bestBid > 0 && bestAsk > 0) (bestBid + bestAsk) / 2.0 else maxOf(bestBid, bestAsk)
                val spreadPct = if (midPrice > 0) ((bestAsk - bestBid) / midPrice) * 100.0 else 0.0
                val totalBidVol = bids.sumOf { it.amount }
                val totalAskVol = asks.sumOf { it.amount }
                val totalVol = totalBidVol + totalAskVol
                val imbalancePct = if (totalVol > 0) ((totalBidVol - totalAskVol) / totalVol) * 100.0 else 0.0
                val bidPressurePct = if (totalVol > 0) (totalBidVol / totalVol) * 100.0 else 50.0

                Result.success(
                    OrderBookData(
                        symbol = symbol,
                        bids = bids,
                        asks = asks,
                        spreadPct = Math.round(spreadPct * 1000.0) / 1000.0,
                        microprice = Math.round(midPrice * 100.0) / 100.0,
                        imbalancePct = Math.round(imbalancePct * 10.0) / 10.0,
                        bidPressurePct = Math.round(bidPressurePct * 10.0) / 10.0,
                        depth10bpsUsd = totalVol * midPrice,
                        sequenceNumber = dto.lastUpdateId ?: System.currentTimeMillis(),
                        isSynced = true
                    )
                )
            } else {
                Result.failure(Exception("Failed to fetch order book for $symbol: HTTP ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Fetches kline candlestick history from exchange.
     */
    suspend fun fetchKlines(symbol: String, interval: String = "1h", limit: Int = 30): Result<List<CandleStick>> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.getKlines(symbol, interval, limit)
            if (response.isSuccessful && response.body() != null) {
                val list = mutableListOf<CandleStick>()
                response.body()!!.forEach { rawList ->
                    val time = (rawList.getOrNull(0) as? Number)?.toLong() ?: 0L
                    val open = (rawList.getOrNull(1) as? String)?.toDoubleOrNull() ?: 0.0
                    val high = (rawList.getOrNull(2) as? String)?.toDoubleOrNull() ?: 0.0
                    val low = (rawList.getOrNull(3) as? String)?.toDoubleOrNull() ?: 0.0
                    val close = (rawList.getOrNull(4) as? String)?.toDoubleOrNull() ?: 0.0
                    val vol = (rawList.getOrNull(5) as? String)?.toDoubleOrNull() ?: 0.0
                    list.add(
                        CandleStick(
                            timestamp = time,
                            open = open,
                            high = high,
                            low = low,
                            close = close,
                            volume = vol
                        )
                    )
                }
                Result.success(list)
            } else {
                Result.failure(Exception("Failed to fetch klines: HTTP ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
