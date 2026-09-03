package com.example.ui.screens

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.ui.components.ForecastFanChart
import com.example.ui.theme.*
import com.example.ui.viewmodel.CryptoScopeViewModel

@Composable
fun ChartTerminalScreen(viewModel: CryptoScopeViewModel) {
    val uiState by viewModel.uiState.collectAsState()
    val isDark = uiState.isDarkTheme
    val bgColor = if (isDark) DarkBackground else LightBackground
    val cardColor = if (isDark) DarkSurface else LightSurface
    val borderColor = if (isDark) DarkBorder else LightBorder
    val textColor = if (isDark) DarkTextPrimary else LightTextPrimary
    val textMutedColor = if (isDark) DarkTextMuted else LightTextMuted

    val livePrices by viewModel.repository.livePrices.collectAsState()
    val prediction = remember(livePrices, uiState.selectedAsset, uiState.selectedHorizon) {
        viewModel.repository.getPrediction(uiState.selectedAsset, uiState.selectedHorizon)
    }
    val candles = remember(uiState.selectedAsset) {
        viewModel.repository.getCandles(uiState.selectedAsset, 32)
    }

    val timeframes = listOf("1m", "5m", "15m", "1h", "4h", "1d")
    var selectedTimeframe by remember { mutableStateOf("1h") }
    var activeOverlayTab by remember { mutableStateOf("FORECAST FAN") }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(bgColor)
            .verticalScroll(rememberScrollState())
            .testTag("chart_terminal_screen")
    ) {
        // Timeframe selector bar
        LazyRow(
            horizontalArrangement = Arrangement.spacedBy(6.dp),
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 8.dp)
        ) {
            items(timeframes) { tf ->
                val isSelected = selectedTimeframe == tf
                Surface(
                    shape = RoundedCornerShape(8.dp),
                    color = if (isSelected) BrandBlue else (if (isDark) DarkSurfaceRaised else LightSurfaceRaised),
                    border = BorderStroke(1.dp, if (isSelected) BrandBlue else borderColor),
                    modifier = Modifier.clickable { selectedTimeframe = tf }
                ) {
                    Text(
                        text = tf,
                        fontSize = 11.sp,
                        fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Medium,
                        color = if (isSelected) Color.White else textMutedColor,
                        modifier = Modifier.padding(horizontal = 12.dp, vertical = 5.dp)
                    )
                }
            }
        }

        // Main Chart Canvas with Candlesticks, Forecast Fan & Volume
        ForecastFanChart(
            candles = candles,
            prediction = prediction,
            modifier = Modifier
                .fillMaxWidth()
                .height(280.dp),
            showForecastFan = (activeOverlayTab == "FORECAST FAN")
        )

        Spacer(modifier = Modifier.height(10.dp))

        // Overlay Toggle Row
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            listOf("FORECAST FAN", "AI SIGNALS", "LEVELS").forEach { tab ->
                val isSelected = activeOverlayTab == tab
                Surface(
                    shape = RoundedCornerShape(16.dp),
                    color = if (isSelected) BrandBlue else (if (isDark) DarkSurfaceRaised else LightSurfaceRaised),
                    border = BorderStroke(1.dp, if (isSelected) BrandBlue else borderColor),
                    modifier = Modifier.clickable { activeOverlayTab = tab }
                ) {
                    Text(
                        text = tab,
                        fontSize = 10.sp,
                        fontWeight = FontWeight.Bold,
                        color = if (isSelected) Color.White else textMutedColor,
                        modifier = Modifier.padding(horizontal = 12.dp, vertical = 5.dp)
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(14.dp))

        // Secondary Microstructure Indicator Panels
        Text("Real-Time Microstructure Panels", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = textColor)
        Spacer(modifier = Modifier.height(8.dp))

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            TerminalMetricPanel("Volume (24H)", "$1.82B", "+3.8%", true, cardColor, borderColor, textColor, textMutedColor, Modifier.weight(1f))
            TerminalMetricPanel("Funding Rate", "0.0091%", "Annualized 8.4%", false, cardColor, borderColor, textColor, textMutedColor, Modifier.weight(1f))
        }
        Spacer(modifier = Modifier.height(10.dp))
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            TerminalMetricPanel("Book Imbalance", "+21%", "Bid Skew (+1.8σ)", true, cardColor, borderColor, textColor, textMutedColor, Modifier.weight(1f))
            TerminalMetricPanel("Liquidations", "$38.2M", "Short Cluster Impending", false, cardColor, borderColor, textColor, textMutedColor, Modifier.weight(1f))
        }
    }
}

@Composable
private fun TerminalMetricPanel(
    title: String,
    value: String,
    detail: String,
    isPositive: Boolean,
    cardColor: Color,
    borderColor: Color,
    textColor: Color,
    textMutedColor: Color,
    modifier: Modifier = Modifier
) {
    Surface(
        shape = RoundedCornerShape(12.dp),
        color = cardColor,
        border = BorderStroke(1.dp, borderColor),
        modifier = modifier
    ) {
        Column(modifier = Modifier.padding(12.dp)) {
            Text(title, fontSize = 10.sp, color = textMutedColor)
            Spacer(modifier = Modifier.height(4.dp))
            Text(value, fontSize = 15.sp, fontWeight = FontWeight.Bold, color = textColor)
            Spacer(modifier = Modifier.height(2.dp))
            Text(detail, fontSize = 10.sp, fontWeight = FontWeight.SemiBold, color = if (isPositive) SemanticPositive else BrandBlue)
        }
    }
}
