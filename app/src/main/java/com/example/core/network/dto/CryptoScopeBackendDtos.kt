package com.example.core.network.dto

import com.squareup.moshi.Json
import com.squareup.moshi.JsonClass

/**
 * Backend UI-Contract DTOs mapping to CryptoScope AI FastAPI Gateway (/api/v1/...)
 */

@JsonClass(generateAdapter = true)
data class MarketOverviewResponseDto(
    @Json(name = "fear_and_greed") val fearAndGreed: FearGreedSummaryDto? = null,
    @Json(name = "futures_overview") val futuresOverview: FuturesSummaryDto? = null,
    @Json(name = "liquidations_24h") val liquidations24h: LiquidationsSummaryDto? = null,
    @Json(name = "contract_radar") val contractRadar: ContractRadarAlertDto? = null,
    @Json(name = "btc_dominance") val btcDominance: BtcDominanceDto? = null,
    @Json(name = "altcoin_season") val altcoinSeason: AltcoinSeasonDto? = null,
    @Json(name = "market_regime") val marketRegime: MarketRegimeDto? = null
)

@JsonClass(generateAdapter = true)
data class FearGreedSummaryDto(
    @Json(name = "value") val value: Int = 50,
    @Json(name = "classification") val classification: String = "Neutral",
    @Json(name = "change_24h") val change24h: Int = 0,
    @Json(name = "updated_at") val updatedAt: String? = null
)

@JsonClass(generateAdapter = true)
data class FuturesSummaryDto(
    @Json(name = "total_open_interest_usd") val totalOpenInterestUsd: Double = 0.0,
    @Json(name = "total_open_interest_formatted") val totalOpenInterestFormatted: String = "$0.00",
    @Json(name = "open_interest_change_24h_pct") val openInterestChange24hPct: Double = 0.0,
    @Json(name = "total_24h_volume_usd") val total24hVolumeUsd: Double = 0.0,
    @Json(name = "total_24h_volume_formatted") val total24hVolumeFormatted: String = "$0.00",
    @Json(name = "volume_change_24h_pct") val volumeChange24hPct: Double = 0.0,
    @Json(name = "long_short_ratio") val longShortRatio: Double = 1.0,
    @Json(name = "long_short_change_24h_pct") val longShortChange24hPct: Double = 0.0,
    @Json(name = "long_account_pct") val longAccountPct: Double = 50.0,
    @Json(name = "short_account_pct") val shortAccountPct: Double = 50.0,
    @Json(name = "taker_buy_sell_ratio") val takerBuySellRatio: Double = 1.0
)

@JsonClass(generateAdapter = true)
data class LiquidationsSummaryDto(
    @Json(name = "long_liquidations_usd") val longLiquidationsUsd: Double = 0.0,
    @Json(name = "long_liquidations_formatted") val longLiquidationsFormatted: String = "$0.00",
    @Json(name = "short_liquidations_usd") val shortLiquidationsUsd: Double = 0.0,
    @Json(name = "short_liquidations_formatted") val shortLiquidationsFormatted: String = "$0.00",
    @Json(name = "total_liquidations_usd") val totalLiquidationsUsd: Double = 0.0,
    @Json(name = "imbalance_ratio") val imbalanceRatio: Double = 1.0
)

@JsonClass(generateAdapter = true)
data class BtcDominanceDto(
    @Json(name = "dominance_pct") val dominancePct: Double = 50.0,
    @Json(name = "change_24h_pct") val change24hPct: Double = 0.0
)

@JsonClass(generateAdapter = true)
data class AltcoinSeasonDto(
    @Json(name = "index") val index: Int = 50,
    @Json(name = "classification") val classification: String = "Neutral"
)

@JsonClass(generateAdapter = true)
data class MarketRegimeDto(
    @Json(name = "regime") val regime: String = "NORMAL",
    @Json(name = "confidence") val confidence: Double = 0.8
)

@JsonClass(generateAdapter = true)
data class ContractRadarAlertDto(
    @Json(name = "symbol") val symbol: String,
    @Json(name = "asset") val asset: String,
    @Json(name = "risk_score") val riskScore: Int = 50,
    @Json(name = "dominant_side") val dominantSide: String = "LONGS_AT_RISK",
    @Json(name = "liquidation_pool_price") val liquidationPoolPrice: Double = 0.0,
    @Json(name = "current_price") val currentPrice: Double = 0.0,
    @Json(name = "distance_pct") val distancePct: Double = 0.0,
    @Json(name = "oi_surge_24h_pct") val oiSurge24hPct: Double = 0.0,
    @Json(name = "funding_rate_pct") val fundingRatePct: Double = 0.0,
    @Json(name = "trigger_reason") val triggerReason: String = "",
    @Json(name = "severity") val severity: String = "MEDIUM"
)

@JsonClass(generateAdapter = true)
data class EtfOverviewDto(
    @Json(name = "total_aum_usd") val totalAumUsd: Double = 0.0,
    @Json(name = "total_net_inflow_24h_usd") val totalNetInflow24hUsd: Double = 0.0,
    @Json(name = "btc_etf_aum_usd") val btcEtfAumUsd: Double = 0.0,
    @Json(name = "eth_etf_aum_usd") val ethEtfAumUsd: Double = 0.0,
    @Json(name = "active_etf_count") val activeEtfCount: Int = 11
)

@JsonClass(generateAdapter = true)
data class RankingItemDto(
    @Json(name = "rank") val rank: Int = 1,
    @Json(name = "canonical_symbol") val canonicalSymbol: String = "",
    @Json(name = "symbol") val symbol: String = "",
    @Json(name = "asset") val asset: String = "",
    @Json(name = "price") val price: Double = 0.0,
    @Json(name = "price_change_24h_pct") val priceChange24hPct: Double = 0.0,
    @Json(name = "volume_24h_usd") val volume24hUsd: Double = 0.0,
    @Json(name = "open_interest_usd") val openInterestUsd: Double = 0.0,
    @Json(name = "funding_rate_pct") val fundingRatePct: Double = 0.0,
    @Json(name = "basis_bps") val basisBps: Double = 0.0
)

@JsonClass(generateAdapter = true)
data class RankingsResponseDto(
    @Json(name = "type") val type: String = "volume",
    @Json(name = "items") val items: List<RankingItemDto> = emptyList()
)

@JsonClass(generateAdapter = true)
data class ScreenerItemDto(
    @Json(name = "rank") val rank: Int = 1,
    @Json(name = "symbol") val symbol: String = "",
    @Json(name = "asset") val asset: String = "",
    @Json(name = "price") val price: Double = 0.0,
    @Json(name = "change_24h_pct") val change24hPct: Double = 0.0,
    @Json(name = "volume_24h_usd") val volume24hUsd: Double = 0.0,
    @Json(name = "open_interest_usd") val openInterestUsd: Double = 0.0,
    @Json(name = "funding_rate_pct") val fundingRatePct: Double = 0.0,
    @Json(name = "volatility_24h_pct") val volatility24hPct: Double = 0.0,
    @Json(name = "rsi_14") val rsi14: Double = 50.0,
    @Json(name = "cvd_delta_usd") val cvdDeltaUsd: Double = 0.0,
    @Json(name = "exchange") val exchange: String = "BINANCE"
)

@JsonClass(generateAdapter = true)
data class ScreenerResponseDto(
    @Json(name = "total_count") val totalCount: Int = 0,
    @Json(name = "count") val count: Int = 0,
    @Json(name = "items") val items: List<ScreenerItemDto> = emptyList()
)

@JsonClass(generateAdapter = true)
data class AiPredictionDto(
    @Json(name = "symbol") val symbol: String,
    @Json(name = "horizon") val horizon: String = "15m",
    @Json(name = "direction") val direction: String = "FLAT",
    @Json(name = "confidence_pct") val confidencePct: Double = 50.0,
    @Json(name = "expected_return_pct") val expectedReturnPct: Double = 0.0,
    @Json(name = "forecast_price") val forecastPrice: Double = 0.0,
    @Json(name = "uncertainty_score") val uncertaintyScore: Double = 0.2,
    @Json(name = "should_abstain") val shouldAbstain: Boolean = false,
    @Json(name = "abstention_reason") val abstentionReason: String? = null
)

@JsonClass(generateAdapter = true)
data class NewsItemDto(
    @Json(name = "id") val id: String,
    @Json(name = "title") val title: String,
    @Json(name = "summary") val summary: String,
    @Json(name = "source") val source: String,
    @Json(name = "category") val category: String,
    @Json(name = "sentiment") val sentiment: String,
    @Json(name = "sentiment_score") val sentimentScore: Double = 0.0,
    @Json(name = "published_at") val publishedAt: String,
    @Json(name = "url") val url: String
)

@JsonClass(generateAdapter = true)
data class MarketEventItemDto(
    @Json(name = "id") val id: String,
    @Json(name = "title") val title: String,
    @Json(name = "date") val date: String,
    @Json(name = "impact") val impact: String,
    @Json(name = "description") val description: String
)

@JsonClass(generateAdapter = true)
data class ProviderStatusDto(
    @Json(name = "provider_name") val providerName: String,
    @Json(name = "category") val category: String,
    @Json(name = "status") val status: String,
    @Json(name = "latency_ms") val latencyMs: Double = 0.0,
    @Json(name = "error_rate_pct") val errorRatePct: Double = 0.0,
    @Json(name = "rate_limit_remaining_pct") val rateLimitRemainingPct: Double = 100.0
)

@JsonClass(generateAdapter = true)
data class UserProfileDto(
    @Json(name = "user_id") val userId: String = "",
    @Json(name = "email") val email: String? = null,
    @Json(name = "display_name") val displayName: String? = null,
    @Json(name = "avatar_url") val avatarUrl: String? = null,
    @Json(name = "timezone") val timezone: String = "UTC",
    @Json(name = "preferred_currency") val preferredCurrency: String = "USD",
    @Json(name = "default_asset") val defaultAsset: String = "BTC",
    @Json(name = "default_horizon") val defaultHorizon: String = "1h",
    @Json(name = "theme") val theme: String = "dark",
    @Json(name = "language") val language: String = "en"
)

@JsonClass(generateAdapter = true)
data class UserProfileResponseDto(
    @Json(name = "success") val success: Boolean = true,
    @Json(name = "data") val data: UserProfileDto? = null
)

@JsonClass(generateAdapter = true)
data class WatchlistItemDto(
    @Json(name = "id") val id: Int = 0,
    @Json(name = "symbol") val symbol: String = "",
    @Json(name = "notes") val notes: String? = null,
    @Json(name = "created_at") val createdAt: String? = null
)

@JsonClass(generateAdapter = true)
data class WatchlistResponseDto(
    @Json(name = "success") val success: Boolean = true,
    @Json(name = "data") val data: List<WatchlistItemDto> = emptyList()
)

@JsonClass(generateAdapter = true)
data class AlertItemDto(
    @Json(name = "id") val id: String = "",
    @Json(name = "symbol") val symbol: String = "",
    @Json(name = "horizon") val horizon: String = "1h",
    @Json(name = "min_confidence") val minConfidence: Int = 80,
    @Json(name = "signal_type") val signalType: String = "LONG",
    @Json(name = "is_active") val isActive: Boolean = true,
    @Json(name = "created_at") val createdAt: String? = null
)

@JsonClass(generateAdapter = true)
data class AlertsResponseDto(
    @Json(name = "success") val success: Boolean = true,
    @Json(name = "data") val data: List<AlertItemDto> = emptyList()
)

@JsonClass(generateAdapter = true)
data class AlertResponseDto(
    @Json(name = "success") val success: Boolean = true,
    @Json(name = "data") val data: AlertItemDto? = null
)

