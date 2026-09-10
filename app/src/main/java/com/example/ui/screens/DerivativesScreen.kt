package com.example.ui.screens

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
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
import com.example.ui.components.Sparkline
import com.example.ui.theme.*
import com.example.ui.viewmodel.CryptoScopeViewModel

@Composable
fun DerivativesScreen(viewModel: CryptoScopeViewModel) {
    val uiState by viewModel.uiState.collectAsState()
    val isDark = uiState.isDarkTheme
    val bgColor = if (isDark) DarkBackground else LightBackground
    val cardColor = if (isDark) DarkSurface else LightSurface
    val borderColor = if (isDark) DarkBorder else LightBorder
    val textColor = if (isDark) DarkTextPrimary else LightTextPrimary
    val textMutedColor = if (isDark) DarkTextMuted else LightTextMuted

    val liveFundingRates by viewModel.repository.liveFundingRates.collectAsState()
    val liveOpenInterests by viewModel.repository.liveOpenInterests.collectAsState()

    val symbol = uiState.selectedAsset.name
    val liveFunding = liveFundingRates[symbol]
    val liveOi = liveOpenInterests[symbol]

    val derivatives = remember(uiState.selectedAsset, liveFunding, liveOi) {
        viewModel.repository.getDerivatives(uiState.selectedAsset)
    }
    val multiFunding = remember(uiState.selectedAsset, liveFunding) {
        viewModel.repository.getMultiExchangeFunding(uiState.selectedAsset)
    }
    val optionsAnalytics = remember(uiState.selectedAsset) {
        viewModel.repository.getOptionsAnalytics(uiState.selectedAsset)
    }
    val orderFlow = remember(uiState.selectedAsset) {
        viewModel.repository.getOrderFlowAnalytics(uiState.selectedAsset)
    }

    val countdown = viewModel.getNextFundingCountdown(symbol)

    var activeSubTab by remember { mutableStateOf("Funding") }
    val tabs = listOf("Funding", "Multi-Venue", "Order Flow", "Options")

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(bgColor)
            .verticalScroll(rememberScrollState())
            .testTag("derivatives_screen")
    ) {
        // Sub tabs
        Row(
            modifier = Modifier.fillMaxWidth().padding(bottom = 12.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            tabs.forEach { tab ->
                val isSelected = activeSubTab == tab
                Surface(
                    shape = RoundedCornerShape(16.dp),
                    color = if (isSelected) BrandBlue else (if (isDark) DarkSurfaceRaised else LightSurfaceRaised),
                    border = BorderStroke(1.dp, if (isSelected) BrandBlue else borderColor),
                    modifier = Modifier.clickable { activeSubTab = tab }
                ) {
                    Text(
                        text = tab,
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Bold,
                        color = if (isSelected) Color.White else textMutedColor,
                        modifier = Modifier.padding(horizontal = 14.dp, vertical = 5.dp)
                    )
                }
            }
        }

        // Top Summary Cards
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            Surface(
                shape = RoundedCornerShape(12.dp),
                color = cardColor,
                border = BorderStroke(1.dp, borderColor),
                modifier = Modifier.weight(1f)
            ) {
                Column(modifier = Modifier.padding(12.dp)) {
                    Text("Current Funding Rate", fontSize = 10.sp, color = textMutedColor)
                    Spacer(modifier = Modifier.height(4.dp))
                    Text("${String.format(java.util.Locale.US, "%.4f", derivatives.currentFunding * 100)}%", fontSize = 16.sp, fontWeight = FontWeight.Bold, color = textColor)
                    Text("8h countdown $countdown", fontSize = 9.sp, color = textMutedColor)
                }
            }

            Surface(
                shape = RoundedCornerShape(12.dp),
                color = cardColor,
                border = BorderStroke(1.dp, borderColor),
                modifier = Modifier.weight(1f)
            ) {
                Column(modifier = Modifier.padding(12.dp)) {
                    Text("Funding 7d Z-Score", fontSize = 10.sp, color = textMutedColor)
                    Spacer(modifier = Modifier.height(4.dp))
                    Text("+${derivatives.fundingZScore}", fontSize = 16.sp, fontWeight = FontWeight.Bold, color = BrandBlue)
                    Text("Moderately elevated", fontSize = 9.sp, color = BrandBlue)
                }
            }
        }

        Spacer(modifier = Modifier.height(14.dp))

        when (activeSubTab) {
            "Multi-Venue" -> {
                // Multi-Venue cross-exchange funding matrix
                Surface(
                    shape = RoundedCornerShape(14.dp),
                    color = cardColor,
                    border = BorderStroke(1.dp, borderColor),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(modifier = Modifier.padding(14.dp)) {
                        Text("Cross-Exchange Funding & OI Matrix", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = textColor)
                        Spacer(modifier = Modifier.height(10.dp))

                        multiFunding.forEachIndexed { index, venue ->
                            Row(
                                modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Column {
                                    Text(venue.exchange, fontSize = 12.sp, fontWeight = FontWeight.SemiBold, color = textColor)
                                    Text("OI $${String.format("%.1f", venue.openInterestUsd / 1e9)}B", fontSize = 10.sp, color = textMutedColor)
                                }
                                Column(horizontalAlignment = Alignment.End) {
                                    Text("${String.format("%.4f", venue.fundingRate * 100)}%", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = textColor)
                                    Text("${String.format("%.1f", venue.annualizedPct)}% APR", fontSize = 10.sp, color = BrandBlue)
                                }
                            }
                            if (index < multiFunding.size - 1) {
                                HorizontalDivider(color = borderColor.copy(alpha = 0.5f), modifier = Modifier.padding(vertical = 4.dp))
                            }
                        }
                    }
                }
            }
            "Order Flow" -> {
                // Order Flow & Microstructure (CVD, Taker ratios)
                Surface(
                    shape = RoundedCornerShape(14.dp),
                    color = cardColor,
                    border = BorderStroke(1.dp, borderColor),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(modifier = Modifier.padding(14.dp)) {
                        Text("Order Flow & Microstructure Dynamics", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = textColor)
                        Spacer(modifier = Modifier.height(10.dp))

                        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                            Text("Spot CVD (24h)", fontSize = 11.sp, color = textMutedColor)
                            Text("+$${String.format("%.1f", orderFlow.spotCvdUsd / 1e6)}M", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = SemanticPositive)
                        }
                        Spacer(modifier = Modifier.height(8.dp))
                        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                            Text("Perp CVD (24h)", fontSize = 11.sp, color = textMutedColor)
                            Text("+$${String.format("%.1f", orderFlow.perpCvdUsd / 1e6)}M", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = SemanticPositive)
                        }
                        Spacer(modifier = Modifier.height(8.dp))
                        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                            Text("Taker Buy Imbalance", fontSize = 11.sp, color = textMutedColor)
                            Text("${String.format("%.1f", orderFlow.takerBuyRatio * 100)}% Buyers", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = SemanticPositive)
                        }
                        Spacer(modifier = Modifier.height(8.dp))
                        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                            Text("Large Trade Dominance", fontSize = 11.sp, color = textMutedColor)
                            Text("${String.format("%.0f", orderFlow.largeTradesDominance * 100)}% Institutional", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = BrandBlue)
                        }
                    }
                }
            }
            "Options" -> {
                // Options Greeks & Max Pain Analytics
                Surface(
                    shape = RoundedCornerShape(14.dp),
                    color = cardColor,
                    border = BorderStroke(1.dp, borderColor),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(modifier = Modifier.padding(14.dp)) {
                        Text("Options Market Intelligence", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = textColor)
                        Spacer(modifier = Modifier.height(10.dp))

                        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                            Text("Put / Call Ratio", fontSize = 11.sp, color = textMutedColor)
                            Text("${optionsAnalytics.putCallRatio} (Bullish Skew)", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = SemanticPositive)
                        }
                        Spacer(modifier = Modifier.height(8.dp))
                        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                            Text("Max Pain Strike", fontSize = 11.sp, color = textMutedColor)
                            Text("$${String.format("%,.0f", optionsAnalytics.maxPainPrice)}", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = textColor)
                        }
                        Spacer(modifier = Modifier.height(8.dp))
                        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                            Text("25-Delta Skew", fontSize = 11.sp, color = textMutedColor)
                            Text("${optionsAnalytics.delta25Skew}% (Calls trading at premium)", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = BrandBlue)
                        }
                        Spacer(modifier = Modifier.height(8.dp))
                        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                            Text("ATM Implied Volatility (DVOL)", fontSize = 11.sp, color = textMutedColor)
                            Text("${optionsAnalytics.impliedVolatilityPct}%", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = textColor)
                        }
                    }
                }
            }
            else -> {
                // Default Funding & Exchange Comparison
                Surface(
                    shape = RoundedCornerShape(14.dp),
                    color = cardColor,
                    border = BorderStroke(1.dp, borderColor),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(modifier = Modifier.padding(14.dp)) {
                        Text("Exchange Comparison", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = textColor)
                        Spacer(modifier = Modifier.height(10.dp))

                        Row(
                            modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Text("Binance", fontSize = 12.sp, fontWeight = FontWeight.Medium, color = textColor)
                            Text("${String.format("%.4f", derivatives.binanceFunding * 100)}%", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = textColor)
                            Text("+0.0012", fontSize = 11.sp, color = SemanticPositive)
                        }
                        HorizontalDivider(color = borderColor.copy(alpha = 0.5f), modifier = Modifier.padding(vertical = 6.dp))
                        Row(
                            modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Text("Bybit", fontSize = 12.sp, fontWeight = FontWeight.Medium, color = textColor)
                            Text("${String.format("%.4f", derivatives.bybitFunding * 100)}%", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = textColor)
                            Text("-0.0009", fontSize = 11.sp, color = SemanticNegative)
                        }
                        HorizontalDivider(color = borderColor.copy(alpha = 0.5f), modifier = Modifier.padding(vertical = 6.dp))
                        Row(
                            modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Text("OKX", fontSize = 12.sp, fontWeight = FontWeight.Medium, color = textColor)
                            Text("${String.format("%.4f", derivatives.okxFunding * 100)}%", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = textColor)
                            Text("+0.0051", fontSize = 11.sp, color = SemanticPositive)
                        }
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(14.dp))

        // Funding Rate History Chart
        Surface(
            shape = RoundedCornerShape(14.dp),
            color = cardColor,
            border = BorderStroke(1.dp, borderColor),
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(modifier = Modifier.padding(14.dp)) {
                Text("Funding Rate History (7d Trend)", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = textColor)
                Spacer(modifier = Modifier.height(12.dp))
                Sparkline(
                    data = derivatives.fundingHistory,
                    modifier = Modifier.fillMaxWidth().height(80.dp),
                    isPositive = true
                )
            }
        }

        Spacer(modifier = Modifier.height(14.dp))

        // Positioning Summary
        Surface(
            shape = RoundedCornerShape(14.dp),
            color = cardColor,
            border = BorderStroke(1.dp, borderColor),
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(modifier = Modifier.padding(14.dp)) {
                Text("Positioning & Open Interest Summary", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = textColor)
                Spacer(modifier = Modifier.height(10.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text("Total Open Interest", fontSize = 11.sp, color = textMutedColor)
                    Text("$${String.format("%.1f", derivatives.openInterestUsd / 1e9)}B (+${derivatives.openInterestDeltaPct}%)", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = SemanticPositive)
                }
                Spacer(modifier = Modifier.height(6.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text("Top Trader L/S Ratio", fontSize = 11.sp, color = textMutedColor)
                    Text("${derivatives.topTraderLongShortRatio} (${derivatives.topTraderSentiment})", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = BrandBlue)
                }
                Spacer(modifier = Modifier.height(6.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text("Basis Annualized", fontSize = 11.sp, color = textMutedColor)
                    Text("${derivatives.annualizedBasisPct}%", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = textColor)
                }
            }
        }

        Spacer(modifier = Modifier.height(40.dp))
    }
}
