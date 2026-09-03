package com.example.ui.screens

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.core.model.CoverageTier
import com.example.core.model.PipelineWorkerStatus
import com.example.core.model.ProviderHealthStatus
import com.example.ui.theme.*
import com.example.ui.viewmodel.CryptoScopeViewModel

@Composable
fun SystemHealthScreen(viewModel: CryptoScopeViewModel) {
    val uiState by viewModel.uiState.collectAsState()
    val isDark = uiState.isDarkTheme
    val bgColor = if (isDark) DarkBackground else LightBackground
    val cardColor = if (isDark) DarkSurface else LightSurface
    val borderColor = if (isDark) DarkBorder else LightBorder
    val textColor = if (isDark) DarkTextPrimary else LightTextPrimary
    val textMutedColor = if (isDark) DarkTextMuted else LightTextMuted

    val providers = remember { viewModel.repository.getProviderHealthList() }
    val workers = remember { viewModel.repository.getPipelineWorkerStatuses() }
    val dataQuality = remember(uiState.selectedAsset) { viewModel.repository.getDataQualityReport(uiState.selectedAsset) }
    val assetRegistry = remember { viewModel.repository.getAssetRegistry() }

    var selectedSection by remember { mutableStateOf("Overview") }
    val sections = listOf("Overview", "Providers (11)", "Pipeline Workers (7)", "Asset Registry (12)")

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(bgColor)
            .padding(horizontal = 16.dp)
            .verticalScroll(rememberScrollState())
            .testTag("system_health_screen")
    ) {
        Spacer(modifier = Modifier.height(12.dp))

        // Top App Bar
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            IconButton(onClick = { viewModel.navigateBack() }, modifier = Modifier.size(32.dp)) {
                Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back", tint = textColor)
            }
            Spacer(modifier = Modifier.width(6.dp))
            Column {
                Text("Enterprise Architecture & Health", fontSize = 18.sp, fontWeight = FontWeight.Bold, color = textColor)
                Text("FastAPI • Event Bus • ML Pipeline • Provider Adapters", fontSize = 10.sp, color = textMutedColor)
            }
        }

        Spacer(modifier = Modifier.height(14.dp))

        // Section Tabs
        LazyRow(
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            modifier = Modifier.fillMaxWidth()
        ) {
            items(sections) { sec ->
                val isSelected = selectedSection == sec
                Surface(
                    shape = RoundedCornerShape(16.dp),
                    color = if (isSelected) BrandBlue else (if (isDark) DarkSurfaceRaised else LightSurfaceRaised),
                    border = BorderStroke(1.dp, if (isSelected) BrandBlue else borderColor),
                    modifier = Modifier.testTag("sec_${sec}")
                ) {
                    Text(
                        text = sec,
                        fontSize = 11.sp,
                        fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Medium,
                        color = if (isSelected) Color.White else textMutedColor,
                        modifier = Modifier
                            .padding(horizontal = 12.dp, vertical = 6.dp)
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Risk Circuit Breaker Control Card
        Surface(
            shape = RoundedCornerShape(14.dp),
            color = cardColor,
            border = BorderStroke(1.dp, if (uiState.circuitBreakerTriggered) SemanticNegative else borderColor),
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column(modifier = Modifier.weight(1f)) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(
                                imageVector = if (uiState.circuitBreakerTriggered) Icons.Default.Shield else Icons.Default.CheckCircle,
                                contentDescription = null,
                                tint = if (uiState.circuitBreakerTriggered) SemanticNegative else SemanticPositive,
                                modifier = Modifier.size(16.dp)
                            )
                            Spacer(modifier = Modifier.width(6.dp))
                            Text(
                                text = "GLOBAL RISK CIRCUIT BREAKER",
                                fontSize = 12.sp,
                                fontWeight = FontWeight.Bold,
                                color = if (uiState.circuitBreakerTriggered) SemanticNegative else textColor
                            )
                        }
                        Spacer(modifier = Modifier.height(4.dp))
                        Text(
                            text = if (uiState.circuitBreakerTriggered) "ACTIVE • Refusing all new orders & automated signals" else "ARMED • Normal market data flow & model execution",
                            fontSize = 11.sp,
                            color = textMutedColor
                        )
                    }
                    Switch(
                        checked = uiState.circuitBreakerTriggered,
                        onCheckedChange = { viewModel.toggleCircuitBreaker() },
                        colors = SwitchDefaults.colors(
                            checkedThumbColor = SemanticNegative,
                            checkedTrackColor = SemanticNegative.copy(alpha = 0.3f)
                        )
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Data Quality & Ingestion Status
        Surface(
            shape = RoundedCornerShape(14.dp),
            color = cardColor,
            border = BorderStroke(1.dp, borderColor),
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "DATA QUALITY ENGINE (${uiState.selectedAsset.name})",
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Bold,
                        color = textMutedColor,
                        letterSpacing = 0.8.sp
                    )
                    Surface(
                        shape = RoundedCornerShape(8.dp),
                        color = if (dataQuality.overallScore >= 90) SemanticPositiveLight else SemanticWarningLight
                    ) {
                        Text(
                            text = "SCORE: ${dataQuality.overallScore}/100",
                            fontSize = 10.sp,
                            fontWeight = FontWeight.Bold,
                            color = if (dataQuality.overallScore >= 90) SemanticPositive else SemanticWarning,
                            modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                        )
                    }
                }
                Spacer(modifier = Modifier.height(10.dp))
                TelemetryRow("Freshness Latency", "${dataQuality.freshnessSec}s", textColor, textMutedColor)
                TelemetryRow("Multi-Provider Consensus", "${dataQuality.providerAgreementPct}%", textColor, textMutedColor)
                TelemetryRow("Candle Continuity Check", if (dataQuality.continuityValid) "PASSED" else "FAILED", if (dataQuality.continuityValid) SemanticPositive else SemanticNegative, textMutedColor)
                TelemetryRow("Orderbook L2 Sequence", if (dataQuality.sequenceValid) "SYNCHRONIZED" else "DESYNC", if (dataQuality.sequenceValid) SemanticPositive else SemanticNegative, textMutedColor)
                TelemetryRow("Missing Features", "${dataQuality.missingFeaturesCount} detected", if (dataQuality.missingFeaturesCount == 0) SemanticPositive else SemanticWarning, textMutedColor)
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Provider Layer Adapters Grid
        Surface(
            shape = RoundedCornerShape(14.dp),
            color = cardColor,
            border = BorderStroke(1.dp, borderColor),
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "DECOUPLED PROVIDER ADAPTERS",
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Bold,
                        color = textMutedColor,
                        letterSpacing = 0.8.sp
                    )
                    Text(
                        text = "11 Healthy",
                        fontSize = 10.sp,
                        fontWeight = FontWeight.Bold,
                        color = SemanticPositive
                    )
                }
                Spacer(modifier = Modifier.height(10.dp))

                providers.forEach { provider ->
                    ProviderStatusRow(provider, textColor, textMutedColor, isDark)
                }
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Backend Pipeline Workers
        Surface(
            shape = RoundedCornerShape(14.dp),
            color = cardColor,
            border = BorderStroke(1.dp, borderColor),
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = "ASYNCHRONOUS PIPELINE WORKERS",
                    fontSize = 11.sp,
                    fontWeight = FontWeight.Bold,
                    color = textMutedColor,
                    letterSpacing = 0.8.sp
                )
                Spacer(modifier = Modifier.height(10.dp))

                workers.forEach { worker ->
                    WorkerStatusRow(worker, textColor, textMutedColor, isDark)
                }
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Universal Asset Registry & Coverage Tiers
        Surface(
            shape = RoundedCornerShape(14.dp),
            color = cardColor,
            border = BorderStroke(1.dp, borderColor),
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = "UNIVERSAL ASSET REGISTRY TIERS",
                    fontSize = 11.sp,
                    fontWeight = FontWeight.Bold,
                    color = textMutedColor,
                    letterSpacing = 0.8.sp
                )
                Spacer(modifier = Modifier.height(10.dp))

                TierSummaryCard("Tier 1: Deep Real-time", "4 Assets (BTC, ETH, SOL, DOGE)", "Full L2/L3 tick trades, orderbook, multi-funding, options & dedicated expert models", SemanticPositive, isDark)
                Spacer(modifier = Modifier.height(6.dp))
                TierSummaryCard("Tier 2: High Liquidity", "75 Assets (BNB, XRP, SUI, AVAX, LINK...)", "Candles, trades, funding, open interest & major derivatives", BrandBlue, isDark)
                Spacer(modifier = Modifier.height(6.dp))
                TierSummaryCard("Tier 3: Broad Universe", "655 Assets (ADA, NEAR, PEPE...)", "Tickers, candles, metadata & baseline global model", textMutedColor, isDark)
            }
        }

        Spacer(modifier = Modifier.height(40.dp))
    }
}

@Composable
private fun ProviderStatusRow(
    provider: ProviderHealthStatus,
    textColor: Color,
    textMutedColor: Color,
    isDark: Boolean
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 5.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Box(
                modifier = Modifier
                    .size(8.dp)
                    .clip(CircleShape)
                    .background(if (provider.isHealthy) SemanticPositive else SemanticNegative)
            )
            Spacer(modifier = Modifier.width(8.dp))
            Column {
                Text(
                    text = provider.name,
                    fontSize = 12.sp,
                    fontWeight = FontWeight.SemiBold,
                    color = textColor
                )
                Text(
                    text = "${provider.category} • Rate Limit: ${provider.rateLimitUsagePct}%",
                    fontSize = 9.sp,
                    color = textMutedColor
                )
            }
        }

        Column(horizontalAlignment = Alignment.End) {
            Text(
                text = "${provider.latencyMs}ms",
                fontSize = 11.sp,
                fontWeight = FontWeight.Bold,
                color = if (provider.latencyMs < 50) SemanticPositive else (if (provider.latencyMs < 100) BrandBlue else SemanticWarning)
            )
            Text(
                text = provider.lastSyncAgo,
                fontSize = 9.sp,
                color = textMutedColor
            )
        }
    }
}

@Composable
private fun WorkerStatusRow(
    worker: PipelineWorkerStatus,
    textColor: Color,
    textMutedColor: Color,
    isDark: Boolean
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 5.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Column(modifier = Modifier.weight(1f)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    text = worker.name,
                    fontSize = 12.sp,
                    fontWeight = FontWeight.SemiBold,
                    color = textColor
                )
                Spacer(modifier = Modifier.width(6.dp))
                Surface(
                    shape = RoundedCornerShape(4.dp),
                    color = if (worker.status == "RUNNING") SemanticPositiveLight else (if (worker.status == "PROCESSING") BrandBlueLight else if (isDark) DarkSurfaceRaised else LightSurfaceRaised)
                ) {
                    Text(
                        text = worker.status,
                        fontSize = 8.sp,
                        fontWeight = FontWeight.Bold,
                        color = if (worker.status == "RUNNING") SemanticPositive else (if (worker.status == "PROCESSING") BrandBlue else textMutedColor),
                        modifier = Modifier.padding(horizontal = 4.dp, vertical = 2.dp)
                    )
                }
            }
            Text(
                text = "${worker.role} • ${worker.throughput}",
                fontSize = 9.sp,
                color = textMutedColor
            )
        }

        Text(
            text = worker.lastHeartbeatAgo,
            fontSize = 9.sp,
            color = textMutedColor
        )
    }
}

@Composable
private fun TierSummaryCard(
    title: String,
    count: String,
    desc: String,
    accentColor: Color,
    isDark: Boolean
) {
    Surface(
        shape = RoundedCornerShape(10.dp),
        color = if (isDark) DarkSurfaceRaised else LightSurfaceRaised,
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(modifier = Modifier.padding(10.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(title, fontSize = 11.sp, fontWeight = FontWeight.Bold, color = accentColor)
                Text(count, fontSize = 10.sp, fontWeight = FontWeight.SemiBold, color = accentColor)
            }
            Spacer(modifier = Modifier.height(2.dp))
            Text(desc, fontSize = 9.sp, color = if (isDark) DarkTextMuted else LightTextMuted, lineHeight = 12.sp)
        }
    }
}

@Composable
private fun TelemetryRow(
    label: String,
    value: String,
    valueColor: Color,
    labelColor: Color
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 3.dp),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(text = label, fontSize = 11.sp, color = labelColor)
        Text(text = value, fontSize = 11.sp, fontWeight = FontWeight.SemiBold, color = valueColor)
    }
}
