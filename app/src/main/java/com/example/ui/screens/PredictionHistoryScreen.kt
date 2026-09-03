package com.example.ui.screens

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Cancel
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.ui.theme.*
import com.example.ui.viewmodel.CryptoScopeViewModel

data class PredictionAuditItem(
    val id: String,
    val timestamp: String,
    val asset: String,
    val horizon: String,
    val signal: String,
    val confidence: Int,
    val expectedReturn: Double,
    val p10: Double,
    val p50: Double,
    val p90: Double,
    val realizedPrice: Double,
    val brierScore: Double,
    val hit: Boolean
)

@Composable
fun PredictionHistoryScreen(viewModel: CryptoScopeViewModel) {
    val uiState by viewModel.uiState.collectAsState()
    val isDark = uiState.isDarkTheme
    val bgColor = if (isDark) DarkBackground else LightBackground
    val cardColor = if (isDark) DarkSurface else LightSurface
    val borderColor = if (isDark) DarkBorder else LightBorder
    val textColor = if (isDark) DarkTextPrimary else LightTextPrimary
    val textMutedColor = if (isDark) DarkTextMuted else LightTextMuted

    val auditLogs = remember {
        listOf(
            PredictionAuditItem("aud-1", "Today 12:00", "BTC", "1H", "LONG", 84, 0.74, 108900.0, 109450.0, 110200.0, 109720.0, 0.12, true),
            PredictionAuditItem("aud-2", "Today 11:00", "ETH", "1H", "LONG", 78, 0.85, 2740.0, 2768.0, 2810.0, 2772.0, 0.14, true),
            PredictionAuditItem("aud-3", "Today 10:00", "SOL", "1H", "NO TRADE", 42, 0.10, 204.0, 207.0, 212.0, 206.5, 0.05, true),
            PredictionAuditItem("aud-4", "Today 09:00", "BTC", "1H", "SHORT", 76, -0.62, 108200.0, 108800.0, 109500.0, 109100.0, 0.28, false),
            PredictionAuditItem("aud-5", "Yesterday 23:00", "BTC", "4H", "LONG", 82, 1.45, 107500.0, 108900.0, 110500.0, 109400.0, 0.11, true)
        )
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(bgColor)
            .padding(horizontal = 16.dp)
            .testTag("prediction_history_screen")
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
                Text(
                    text = "Prediction Audit Log",
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold,
                    color = textColor
                )
                Text(
                    text = "Resolved Probabilistic Forecasts",
                    fontSize = 10.sp,
                    color = textMutedColor
                )
            }
        }

        Spacer(modifier = Modifier.height(14.dp))

        // Brier Metric Banner
        Surface(
            shape = RoundedCornerShape(12.dp),
            color = cardColor,
            border = BorderStroke(1.dp, borderColor),
            modifier = Modifier.fillMaxWidth()
        ) {
            Row(
                modifier = Modifier.padding(14.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text("ROLLING BRIER SCORE", fontSize = 10.sp, fontWeight = FontWeight.Bold, color = textMutedColor)
                    Text("0.138", fontSize = 20.sp, fontWeight = FontWeight.Bold, color = SemanticPositive)
                }
                Column(horizontalAlignment = Alignment.End) {
                    Text("CALIBRATION ACCURACY", fontSize = 10.sp, fontWeight = FontWeight.Bold, color = textMutedColor)
                    Text("79.4% (P10-P90 inside)", fontSize = 14.sp, fontWeight = FontWeight.Bold, color = BrandBlue)
                }
            }
        }

        Spacer(modifier = Modifier.height(12.dp))

        LazyColumn(
            verticalArrangement = Arrangement.spacedBy(10.dp),
            contentPadding = PaddingValues(bottom = 60.dp)
        ) {
            items(auditLogs) { log ->
                Surface(
                    shape = RoundedCornerShape(12.dp),
                    color = cardColor,
                    border = BorderStroke(1.dp, borderColor),
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable { viewModel.openPredictionInspector(log.id) }
                ) {
                    Column(modifier = Modifier.padding(14.dp)) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Text(
                                    text = "${log.asset} ${log.horizon}",
                                    fontSize = 14.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = textColor
                                )
                                Spacer(modifier = Modifier.width(6.dp))
                                Surface(
                                    shape = RoundedCornerShape(4.dp),
                                    color = when (log.signal) {
                                        "LONG" -> SemanticPositiveLight
                                        "SHORT" -> SemanticNegativeLight
                                        else -> if (isDark) DarkSurfaceRaised else LightSurfaceRaised
                                    }
                                ) {
                                    Text(
                                        text = log.signal,
                                        fontSize = 10.sp,
                                        fontWeight = FontWeight.Bold,
                                        color = when (log.signal) {
                                            "LONG" -> SemanticPositive
                                            "SHORT" -> SemanticNegative
                                            else -> textMutedColor
                                        },
                                        modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                                    )
                                }
                            }
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                if (log.hit) {
                                    Icon(Icons.Default.CheckCircle, contentDescription = null, tint = SemanticPositive, modifier = Modifier.size(16.dp))
                                    Spacer(modifier = Modifier.width(4.dp))
                                    Text("RESOLVED HIT", fontSize = 11.sp, fontWeight = FontWeight.Bold, color = SemanticPositive)
                                } else {
                                    Icon(Icons.Default.Cancel, contentDescription = null, tint = SemanticNegative, modifier = Modifier.size(16.dp))
                                    Spacer(modifier = Modifier.width(4.dp))
                                    Text("MISS", fontSize = 11.sp, fontWeight = FontWeight.Bold, color = SemanticNegative)
                                }
                            }
                        }

                        Spacer(modifier = Modifier.height(8.dp))

                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Text(text = log.timestamp, fontSize = 11.sp, color = textMutedColor)
                            Text(text = "Confidence ${log.confidence}% • Brier ${log.brierScore}", fontSize = 11.sp, color = textMutedColor)
                        }

                        Spacer(modifier = Modifier.height(6.dp))

                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Text(
                                text = "Band: $${String.format("%,.0f", log.p10)} - $${String.format("%,.0f", log.p90)}",
                                fontSize = 11.sp,
                                color = textColor
                            )
                            Text(
                                text = "Realized: $${String.format("%,.0f", log.realizedPrice)}",
                                fontSize = 11.sp,
                                fontWeight = FontWeight.SemiBold,
                                color = BrandBlue
                            )
                        }
                    }
                }
            }
        }
    }
}

