package com.example.core.network.dto

import com.squareup.moshi.Json
import com.squareup.moshi.JsonClass

/**
 * 24-hour ticker statistics from public Futures endpoint (/fapi/v1/ticker/24hr)
 */
@JsonClass(generateAdapter = true)
data class Futures24HrTickerDto(
    @Json(name = "symbol") val symbol: String,
    @Json(name = "priceChange") val priceChange: String? = null,
    @Json(name = "priceChangePercent") val priceChangePercent: String? = null,
    @Json(name = "weightedAvgPrice") val weightedAvgPrice: String? = null,
    @Json(name = "lastPrice") val lastPrice: String? = null,
    @Json(name = "lastQty") val lastQty: String? = null,
    @Json(name = "openPrice") val openPrice: String? = null,
    @Json(name = "highPrice") val highPrice: String? = null,
    @Json(name = "lowPrice") val lowPrice: String? = null,
    @Json(name = "volume") val volume: String? = null,
    @Json(name = "quoteVolume") val quoteVolume: String? = null,
    @Json(name = "openTime") val openTime: Long? = null,
    @Json(name = "closeTime") val closeTime: Long? = null,
    @Json(name = "firstId") val firstId: Long? = null,
    @Json(name = "lastId") val lastId: Long? = null,
    @Json(name = "count") val count: Long? = null
)

/**
 * Mark price, index price and real-time funding rate (/fapi/v1/premiumIndex)
 */
@JsonClass(generateAdapter = true)
data class FuturesPremiumIndexDto(
    @Json(name = "symbol") val symbol: String,
    @Json(name = "markPrice") val markPrice: String? = null,
    @Json(name = "indexPrice") val indexPrice: String? = null,
    @Json(name = "estimatedSettlePrice") val estimatedSettlePrice: String? = null,
    @Json(name = "lastFundingRate") val lastFundingRate: String? = null,
    @Json(name = "interestRate") val interestRate: String? = null,
    @Json(name = "nextFundingTime") val nextFundingTime: Long? = null,
    @Json(name = "time") val time: Long? = null
)

/**
 * Open interest statistics for a symbol (/fapi/v1/openInterest)
 */
@JsonClass(generateAdapter = true)
data class FuturesOpenInterestDto(
    @Json(name = "symbol") val symbol: String,
    @Json(name = "openInterest") val openInterest: String? = null,
    @Json(name = "time") val time: Long? = null
)

/**
 * Order book depth snapshot (/fapi/v1/depth)
 */
@JsonClass(generateAdapter = true)
data class FuturesOrderBookDto(
    @Json(name = "lastUpdateId") val lastUpdateId: Long? = null,
    @Json(name = "E") val eventTime: Long? = null,
    @Json(name = "T") val transactionTime: Long? = null,
    @Json(name = "bids") val bids: List<List<String>> = emptyList(),
    @Json(name = "asks") val asks: List<List<String>> = emptyList()
)

/**
 * Top trader long/short account ratio (/futures/data/topLongShortPositionRatio)
 */
@JsonClass(generateAdapter = true)
data class FuturesLongShortRatioDto(
    @Json(name = "symbol") val symbol: String,
    @Json(name = "longShortRatio") val longShortRatio: String? = null,
    @Json(name = "longAccount") val longAccount: String? = null,
    @Json(name = "shortAccount") val shortAccount: String? = null,
    @Json(name = "timestamp") val timestamp: Long? = null
)

/**
 * Symbol filter rules in exchange info
 */
@JsonClass(generateAdapter = true)
data class FuturesSymbolInfoDto(
    @Json(name = "symbol") val symbol: String,
    @Json(name = "pair") val pair: String? = null,
    @Json(name = "contractType") val contractType: String? = null,
    @Json(name = "status") val status: String? = null,
    @Json(name = "baseAsset") val baseAsset: String? = null,
    @Json(name = "quoteAsset") val quoteAsset: String? = null,
    @Json(name = "pricePrecision") val pricePrecision: Int? = null,
    @Json(name = "quantityPrecision") val quantityPrecision: Int? = null
)

/**
 * Futures exchange metadata (/fapi/v1/exchangeInfo)
 */
@JsonClass(generateAdapter = true)
data class FuturesExchangeInfoDto(
    @Json(name = "timezone") val timezone: String? = null,
    @Json(name = "serverTime") val serverTime: Long? = null,
    @Json(name = "symbols") val symbols: List<FuturesSymbolInfoDto> = emptyList()
)
