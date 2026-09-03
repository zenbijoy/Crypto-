package com.example.ui.screens

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.ui.components.ForecastFanChart
import com.example.ui.theme.*
import com.example.ui.viewmodel.CryptoScopeViewModel

@Composable
fun LevelsScreen(viewModel: CryptoScopeViewModel) {
    val uiState by viewModel.uiState.collectAsState()
    val isDark = uiState.isDarkTheme
    val bgColor = if (isDark) DarkBackground else LightBackground
    val cardColor = if (isDark) DarkSurface else LightSurface
    val borderColor = if (isDark) DarkBorder else LightBorder
    val textColor = if (isDark) DarkTextPrimary else LightTextPrimary
    val textMutedColor = if (isDark) DarkTextMuted else LightTextMuted

    val levels = remember(uiState.selectedAsset) {
        viewModel.repository.getMarketStructure(uiState.selectedAsset)
    }
    val candles = remember(uiState.selectedAsset) {
        viewModel.repository.getCandles(uiState.selectedAsset, 24)
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(bgColor)
            .verticalScroll(rememberScrollState())
            .testTag("levels_screen")
    ) {
        // Mini chart with zones
        ForecastFanChart(
            candles = candles,
            prediction = null,
            modifier = Modifier
                .fillMaxWidth()
                .height(180.dp),
            showForecastFan = false
        )

        Spacer(modifier = Modifier.height(14.dp))

        // Resistance Zones
        Text("Resistance Zones (Ask Liquidity & Sell Walls)", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = textColor)
        Spacer(modifier = Modifier.height(8.dp))

        levels.zones.filter { it.isResistance }.forEach { zone ->
            Surface(
                shape = RoundedCornerShape(12.dp),
                color = cardColor,
                border = BorderStroke(1.dp, borderColor),
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(bottom = 8.dp)
            ) {
                Row(
                    modifier = Modifier.padding(14.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text(
                            text = "${(zone.minPrice / 1000).toInt()}K – ${(zone.maxPrice / 1000).toInt()}K",
                            fontSize = 14.sp,
                            fontWeight = FontWeight.Bold,
                            color = SemanticNegative
                        )
                        Text(
                            text = "${zone.touches} touches • ${zone.label}",
                            fontSize = 10.sp,
                            color = textMutedColor
                        )
                    }
                    Surface(
                        shape = RoundedCornerShape(6.dp),
                        color = SemanticNegativeLight
                    ) {
                        Text(
                            text = "${zone.strength} STR",
                            fontSize = 11.sp,
                            fontWeight = FontWeight.Bold,
                            color = SemanticNegative,
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 3.dp)
                        )
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(12.dp))

        // Support Zones
        Text("Support Zones (Bid Liquidity & Buy Clusters)", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = textColor)
        Spacer(modifier = Modifier.height(8.dp))

        levels.zones.filter { !it.isResistance }.forEach { zone ->
            Surface(
                shape = RoundedCornerShape(12.dp),
                color = cardColor,
                border = BorderStroke(1.dp, borderColor),
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(bottom = 8.dp)
            ) {
                Row(
                    modifier = Modifier.padding(14.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text(
                            text = "${(zone.minPrice / 1000).toInt()}K – ${(zone.maxPrice / 1000).toInt()}K",
                            fontSize = 14.sp,
                            fontWeight = FontWeight.Bold,
                            color = SemanticPositive
                        )
                        Text(
                            text = "${zone.touches} touches • ${zone.label}",
                            fontSize = 10.sp,
                            color = textMutedColor
                        )
                    }
                    Surface(
                        shape = RoundedCornerShape(6.dp),
                        color = SemanticPositiveLight
                    ) {
                        Text(
                            text = "${zone.strength} STR",
                            fontSize = 11.sp,
                            fontWeight = FontWeight.Bold,
                            color = SemanticPositive,
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 3.dp)
                        )
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(12.dp))

        // Structure Summary Card
        Surface(
            shape = RoundedCornerShape(12.dp),
            color = cardColor,
            border = BorderStroke(1.dp, borderColor),
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(modifier = Modifier.padding(14.dp)) {
                Text("Market Structure Regimes", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = textColor)
                Spacer(modifier = Modifier.height(10.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text("Trend", fontSize = 11.sp, color = textMutedColor)
                    Text(levels.trend, fontSize = 12.sp, fontWeight = FontWeight.Bold, color = textColor)
                }
                Spacer(modifier = Modifier.height(6.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text("Breakout state", fontSize = 11.sp, color = textMutedColor)
                    Text(levels.structureState, fontSize = 12.sp, fontWeight = FontWeight.SemiBold, color = BrandBlue)
                }
            }
        }
    }
}
