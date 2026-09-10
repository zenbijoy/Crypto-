package com.example.core.network.dto

import com.squareup.moshi.Json
import com.squareup.moshi.JsonClass

/**
 * Standardized ticker price observation across exchange venues
 * (Binance, Bybit, OKX, Coinbase, Kraken, Hyperliquid).
 */
@JsonClass(generateAdapter = true)
data class ExchangeTickerDto(
    @Json(name = "symbol") val symbol: String,
    @Json(name = "provider") val provider: String = "BINANCE",
    @Json(name = "price") val price: Double = 0.0,
    @Json(name = "bid_price") val bidPrice: Double? = null,
    @Json(name = "ask_price") val askPrice: Double? = null,
    @Json(name = "high_24h") val high24h: Double? = null,
    @Json(name = "low_24h") val low24h: Double? = null,
    @Json(name = "volume_24h") val volume24h: Double? = null,
    @Json(name = "quote_volume_24h") val quoteVolume24h: Double? = null,
    @Json(name = "price_change_24h_pct") val priceChange24hPct: Double? = null,
    @Json(name = "timestamp") val timestamp: String? = null
)

/**
 * Envelope wrapper for canonical API responses.
 */
@JsonClass(generateAdapter = true)
data class CanonicalMarketTickerResponseDto(
    @Json(name = "success") val success: Boolean = true,
    @Json(name = "data") val data: ExchangeTickerDto? = null,
    @Json(name = "meta") val meta: Map<String, Any>? = null
)

/**
 * Envelope wrapper for list of canonical market ticker summaries.
 */
@JsonClass(generateAdapter = true)
data class CanonicalMarketSummaryResponseDto(
    @Json(name = "success") val success: Boolean = true,
    @Json(name = "data") val data: List<ExchangeTickerDto> = emptyList(),
    @Json(name = "meta") val meta: Map<String, Any>? = null
)

/**
 * Aggregated order book depth snapshot DTO.
 */
@JsonClass(generateAdapter = true)
data class OrderBookResponseDto(
    @Json(name = "success") val success: Boolean = true,
    @Json(name = "symbol") val symbol: String = "",
    @Json(name = "depth") val depth: Int = 50,
    @Json(name = "data") val data: Map<String, Any>? = null,
    @Json(name = "timestamp") val timestamp: String? = null
)

/**
 * Aggregated derivatives summary DTO.
 */
@JsonClass(generateAdapter = true)
data class DerivativesSummaryResponseDto(
    @Json(name = "success") val success: Boolean = true,
    @Json(name = "data") val data: Map<String, Any>? = null,
    @Json(name = "meta") val meta: Map<String, Any>? = null
)
