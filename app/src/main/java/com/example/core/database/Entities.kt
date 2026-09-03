package com.example.core.database

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "watchlists")
data class WatchlistEntity(
    @PrimaryKey val symbol: String,
    val listCategory: String = "DEFAULT",
    val addedAt: Long = System.currentTimeMillis()
)

@Entity(tableName = "alert_rules")
data class AlertRuleEntity(
    @PrimaryKey val id: String,
    val asset: String,
    val horizon: String,
    val signal: String,
    val minConfidence: Int,
    val minAgreement: Int,
    val minDataQuality: Int,
    val cooldownMinutes: Int,
    val requireExpectedEdge: Boolean,
    val requireRiskEngineAllow: Boolean,
    val status: String,
    val createdAt: Long = System.currentTimeMillis()
)

@Entity(tableName = "paper_positions")
data class PaperPositionEntity(
    @PrimaryKey val id: String,
    val symbol: String,
    val direction: String,
    val entryPrice: Double,
    val markPrice: Double,
    val sizeUsd: Double,
    val leverage: Int,
    val stopLoss: Double,
    val takeProfit: Double,
    val aiConfidence: Int,
    val aiRegime: String,
    val aiModel: String,
    val aiRisk: String,
    val createdAt: Long = System.currentTimeMillis()
)

@Entity(tableName = "market_cache")
data class MarketCacheEntity(
    @PrimaryKey val symbol: String,
    val lastPrice: Double,
    val change24h: Double,
    val volume24h: Double,
    val updatedAt: Long = System.currentTimeMillis()
)
