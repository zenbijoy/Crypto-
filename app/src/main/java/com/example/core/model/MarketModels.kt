package com.example.core.model

import androidx.annotation.Keep

@Keep
enum class AssetSymbol(val code: String, val assetName: String, val basePrice: Double) {
    BTC("BTCUSDT", "Bitcoin", 109420.30),
    ETH("ETHUSDT", "Ethereum", 4386.50),
    SOL("SOLUSDT", "Solana", 208.14),
    BNB("BNBUSDT", "BNB", 812.50),
    XRP("XRPUSDT", "XRP", 3.02),
    DOGE("DOGEUSDT", "Dogecoin", 0.237)
}

@Keep
enum class Horizon(val display: String, val code: String, val description: String) {
    H_1M("1m", "1m", "Microstructure"),
    H_5M("5m", "5m", "Scalping"),
    H_15M("15m", "15m", "Short-Term"),
    H_30M("30m", "30m", "Intraday"),
    H_1H("1h", "1h", "1-Hour"),
    H_4H("4h", "4h", "Session"),
    H_12H("12h", "12h", "Multi-Session"),
    H_1D("24h", "24h", "Daily Swing"),
    H_3D("3d", "3d", "Multi-Day"),
    H_7D("7d", "7d", "Macro Trend")
}

@Keep
enum class SignalType(val title: String) {
    STRONG_LONG("STRONG LONG"),
    LONG("LONG"),
    NEUTRAL("NO-TRADE"),
    SHORT("SHORT"),
    STRONG_SHORT("STRONG SHORT"),
    ABSTAINED("NO SIGNAL / ABSTAINED")
}

@Keep
enum class SignalConfidenceTier(val label: String) {
    HIGH("HIGH-CONFIDENCE"),
    MEDIUM("MEDIUM-CONFIDENCE"),
    LOW("LOW-CONFIDENCE"),
    NO_SIGNAL("NO SIGNAL / ABSTAINED")
}

@Keep
enum class RiskLevel {
    LOW,
    MEDIUM,
    HIGH,
    CRITICAL
}

@Keep
data class SubModelScore(
    val name: String,
    val bullishProb: Double,
    val bearishProb: Double,
    val weight: Double,
    val signal: String
)

@Keep
data class MultiExchangeFunding(
    val exchange: String,
    val fundingRate: Double,
    val annualizedPct: Double,
    val volume24hUsd: Double,
    val openInterestUsd: Double
)

@Keep
data class OptionsAnalytics(
    val symbol: String,
    val putCallRatio: Double,
    val maxPainPrice: Double,
    val delta25Skew: Double,
    val impliedVolatilityPct: Double,
    val totalOpenInterestUsd: Double,
    val totalVolume24hUsd: Double
)

@Keep
data class OrderFlowAnalytics(
    val symbol: String,
    val spotCvdUsd: Double,
    val perpCvdUsd: Double,
    val takerBuyRatio: Double,
    val takerSellRatio: Double,
    val largeTradesDominance: Double,
    val bidDepthUsd: Double,
    val askDepthUsd: Double
)

@Keep
data class MarketItem(
    val symbol: String,
    val asset: String,
    val pair: String,
    val price: Double,
    val markPrice: Double,
    val change24h: Double,
    val volume24h: Double,
    val fundingRate: Double,
    val openInterest: Double,
    val sparkline: List<Double>,
    val marketType: String = "USDT Perp"
)

@Keep
data class CandleStick(
    val timestamp: Long,
    val open: Double,
    val high: Double,
    val low: Double,
    val close: Double,
    val volume: Double
)

@Keep
data class FeatureAttribution(
    val feature: String,
    val impact: Double,
    val isBullish: Boolean,
    val description: String
)

@Keep
data class PredictionForecast(
    val id: String,
    val asset: String,
    val pair: String,
    val horizon: Horizon,
    val currentPrice: Double,
    val expectedReturnPct: Double,
    val signal: SignalType,
    val confidenceTier: SignalConfidenceTier = SignalConfidenceTier.HIGH,
    val confidenceScore: Int, // 0-100 calibrated
    val modelAgreementScore: Int, // 0-100
    val pUp: Double,
    val pSideways: Double,
    val pDown: Double,
    val p10: Double,
    val p25: Double,
    val p50: Double,
    val p75: Double,
    val p90: Double,
    val expectedVolatilityPct: Double,
    val regime: String,
    val dataQualityScore: Int,
    val signalReason: String,
    val riskLevel: RiskLevel,
    val riskWarning: String = "Normal order flow dynamics with bounded volatility",
    val modelTier: String = "Tier-1 Super Model",
    val modelVersion: String,
    val isAbstained: Boolean = false,
    val abstainReason: String? = null,
    val generatedAtUtc: Long,
    val subModels: List<SubModelScore> = emptyList(),
    val attributions: List<FeatureAttribution>
)

@Keep
data class OrderBookEntry(
    val price: Double,
    val amount: Double,
    val total: Double
)

@Keep
data class OrderBookData(
    val symbol: String,
    val bids: List<OrderBookEntry>,
    val asks: List<OrderBookEntry>,
    val spreadPct: Double,
    val microprice: Double,
    val imbalancePct: Double,
    val bidPressurePct: Double,
    val depth10bpsUsd: Double,
    val sequenceNumber: Long,
    val isSynced: Boolean = true
)

@Keep
data class DerivativesData(
    val symbol: String,
    val currentFunding: Double,
    val fundingZScore: Double,
    val openInterestUsd: Double,
    val openInterestDeltaPct: Double,
    val topTraderLongShortRatio: Double,
    val topTraderSentiment: String,
    val annualizedBasisPct: Double,
    val binanceFunding: Double,
    val bybitFunding: Double,
    val okxFunding: Double,
    val fundingHistory: List<Double>
)

@Keep
data class LiquidationClusterItem(
    val priceLevel: Double,
    val volumeUsd: Double,
    val side: String,
    val intensity: Float
)

@Keep
data class LiquidationRecentEvent(
    val side: String,
    val price: Double,
    val amountText: String,
    val timeAgo: String
)

@Keep
data class LiquidationData(
    val symbol: String,
    val longLiq1hUsd: Double,
    val shortLiq1hUsd: Double,
    val pressureScore: Int,
    val statusLabel: String,
    val clusters: List<LiquidationClusterItem>,
    val recentEvents: List<LiquidationRecentEvent>
)

@Keep
data class SupportResistanceZone(
    val isResistance: Boolean,
    val minPrice: Double,
    val maxPrice: Double,
    val strength: Int,
    val touches: Int,
    val label: String
)

@Keep
data class MarketStructureData(
    val symbol: String,
    val trend: String,
    val structureState: String,
    val zones: List<SupportResistanceZone>
)

@Keep
data class NewsItem(
    val id: String,
    val title: String,
    val source: String,
    val timeAgo: String,
    val category: String,
    val sentimentTag: String, // "GREEN", "GOLD", "RED"
    val relevance: Double
)

@Keep
data class SentimentData(
    val symbol: String,
    val sentimentState: String,
    val fearGreedScore: Int,
    val fearGreedLabel: String,
    val eventRisk: String,
    val history: List<Double>,
    val newsList: List<NewsItem>
)

@Keep
data class OnChainData(
    val asset: String,
    val exchangeNetflowBtc: Double,
    val whaleDeposits: String,
    val sopr: Double,
    val mvrv: Double,
    val hashRate: String,
    val activeAddresses: String,
    val trend: List<Double>,
    val takeaways: List<String>
)

@Keep
data class MacroCalendarEvent(
    val name: String,
    val timeOffset: String,
    val impact: String // "HIGH", "MED", "LOW"
)

@Keep
data class MacroData(
    val nextEvent: String,
    val countdown: String,
    val fedFundsRate: String,
    val us10yYield: String,
    val dxyIndex: String,
    val sp500Change: String,
    val goldPrice: String,
    val vix: String,
    val events: List<MacroCalendarEvent>
)

@Keep
data class AlertRuleItem(
    val id: String,
    val asset: String,
    val horizon: String,
    val signal: String,
    val minConfidence: Int,
    val minAgreement: Int,
    val minDataQuality: Int,
    val cooldownMinutes: Int,
    val requireExpectedEdge: Boolean,
    val requireRiskEngineAllow: Boolean,
    val status: String, // "ACTIVE", "TRIGGERED", "PAUSED"
    val createdAtFormatted: String,
    val lastCheckFormatted: String
)

@Keep
data class PaperPositionItem(
    val id: String,
    val symbol: String,
    val direction: String, // "LONG" or "SHORT"
    val entryPrice: Double,
    val markPrice: Double,
    val sizeUsd: Double,
    val leverage: Int,
    val unrealizedPnl: Double,
    val unrealizedPnlPct: Double,
    val stopLoss: Double,
    val takeProfit: Double,
    val aiConfidence: Int,
    val aiRegime: String,
    val aiModel: String,
    val aiRisk: String
)

@Keep
data class NotificationItem(
    val id: String,
    val title: String,
    val subtitle: String,
    val timeAgo: String,
    val type: String, // "SIGNAL", "SYSTEM", "MACRO"
    val isUnread: Boolean
)

@Keep
data class HistoricalPredictionAudit(
    val id: String,
    val asset: String,
    val horizon: String,
    val signal: String,
    val confidence: Int,
    val predictedReturnPct: Double,
    val actualReturnPct: Double,
    val isWin: Boolean,
    val isAbstained: Boolean,
    val timestampFormatted: String,
    val modelVersion: String,
    val knownPriceAtT: Double,
    val fundingAtT: Double,
    val oiDeltaAtT: Double,
    val topAttributions: List<FeatureAttribution>
)

@Keep
enum class CoverageTier(val label: String, val description: String) {
    TIER_1_DEEP("Tier 1: Deep Real-time", "Full L2/L3 orderbook, tick trades, multi-funding, options & dedicated expert models (BTC, ETH, SOL, DOGE)"),
    TIER_2_HIGH_LIQUIDITY("Tier 2: High Liquidity", "Candles, trades, funding, OI & major derivatives (~75 assets)"),
    TIER_3_BROAD("Tier 3: Broad Universe", "Ticker, candles, metadata & baseline global model (~650+ assets)")
}

@Keep
data class ProviderHealthStatus(
    val name: String,
    val category: String, // Exchange, Derivatives, Macro, On-chain, News
    val status: String, // HEALTHY, DEGRADED, RATE_LIMITED
    val latencyMs: Int,
    val isHealthy: Boolean,
    val rateLimitUsagePct: Int,
    val lastSyncAgo: String
)

@Keep
data class PipelineWorkerStatus(
    val name: String,
    val role: String,
    val status: String, // RUNNING, IDLE, PROCESSING
    val throughput: String,
    val lastHeartbeatAgo: String,
    val isHealthy: Boolean = true
)

@Keep
data class ChampionChallengerModel(
    val modelId: String,
    val asset: String,
    val horizon: String,
    val algorithm: String, // XGBoost + TFT Ensemble, LightGBM, CatBoost, TCN
    val role: String, // CHAMPION (Production), CHALLENGER (Shadow), EXPERIMENTAL
    val brierScore: Double,
    val hitRatePct: Double,
    val outOfSampleSharpe: Double,
    val status: String
)

@Keep
data class DataQualityReport(
    val asset: String,
    val overallScore: Int, // 0-100
    val freshnessSec: Double,
    val providerAgreementPct: Double,
    val continuityValid: Boolean,
    val sequenceValid: Boolean,
    val missingFeaturesCount: Int,
    val statusText: String
)

@Keep
data class MarketIntelligenceReport(
    val asset: String,
    val regime: String,
    val leverageIndex: String, // ELEVATED, NORMAL, LOW
    val liquidationRisk: String, // LOW, MEDIUM, HIGH
    val marketBreadth: Double,
    val buyPressure: Double,
    val whaleDivergence: String,
    val anomalyScore: Double
)

@Keep
data class AssetRegistryItem(
    val canonicalSymbol: String,
    val name: String,
    val tier: CoverageTier,
    val binanceSymbol: String,
    val bybitSymbol: String,
    val okxSymbol: String,
    val coinbaseSymbol: String,
    val hyperliquidSymbol: String,
    val isLive: Boolean = true
)
