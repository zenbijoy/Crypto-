package com.example.ui.screens

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.ui.theme.*
import com.example.ui.viewmodel.CryptoScopeViewModel
import com.example.ui.viewmodel.ScreenRoute

@Composable
fun PaperDashboardScreen(viewModel: CryptoScopeViewModel) {
    val uiState by viewModel.uiState.collectAsState()
    val isDark = uiState.isDarkTheme
    val bgColor = if (isDark) DarkBackground else LightBackground
    val cardColor = if (isDark) DarkSurface else LightSurface
    val borderColor = if (isDark) DarkBorder else LightBorder
    val textColor = if (isDark) DarkTextPrimary else LightTextPrimary
    val textMutedColor = if (isDark) DarkTextMuted else LightTextMuted

    val livePrices by viewModel.repository.livePrices.collectAsState()
    val positions by viewModel.repository.getPaperPositions().collectAsState(initial = emptyList())

    val filterTabs = listOf("Positions (${positions.size})", "Orders (0)", "History (14)")
    var selectedTab by remember { mutableStateOf("Positions (${positions.size})") }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(bgColor)
            .padding(horizontal = 16.dp)
            .testTag("paper_dashboard_screen")
    ) {
        Spacer(modifier = Modifier.height(12.dp))

        // Top Header
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column {
                Text("Paper Trading", fontSize = 20.sp, fontWeight = FontWeight.Bold, color = textColor)
                Text("Simulation • Realistic Slippage & Fees", fontSize = 10.sp, color = textMutedColor)
            }
            Button(
                onClick = { viewModel.navigateTo(ScreenRoute.PAPER_ORDER_TICKET) },
                colors = ButtonDefaults.buttonColors(containerColor = BrandBlue, contentColor = Color.White),
                shape = RoundedCornerShape(8.dp),
                contentPadding = PaddingValues(horizontal = 12.dp, vertical = 6.dp),
                modifier = Modifier.height(36.dp).testTag("new_order_button")
            ) {
                Icon(Icons.Default.Add, contentDescription = null, modifier = Modifier.size(14.dp))
                Spacer(modifier = Modifier.width(4.dp))
                Text("NEW ORDER", fontSize = 11.sp, fontWeight = FontWeight.Bold)
            }
        }

        Spacer(modifier = Modifier.height(14.dp))

        // Balance & PnL Hero Card
        Surface(
            shape = RoundedCornerShape(16.dp),
            color = cardColor,
            border = BorderStroke(1.dp, borderColor),
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("VIRTUAL BALANCE", fontSize = 10.sp, fontWeight = FontWeight.Bold, color = textMutedColor, letterSpacing = 0.5.sp)
                Spacer(modifier = Modifier.height(4.dp))
                Text("$${String.format("%,.2f", uiState.paperEquity)}", fontSize = 28.sp, fontWeight = FontWeight.Bold, color = textColor)
                Spacer(modifier = Modifier.height(4.dp))
                Text("+$${String.format("%.2f", uiState.paperTotalPnl)} (+${uiState.paperTotalPnlPct}%) total paper return", fontSize = 11.sp, fontWeight = FontWeight.SemiBold, color = SemanticPositive)

                HorizontalDivider(color = borderColor, modifier = Modifier.padding(vertical = 12.dp))

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Column {
                        Text("Margin Used", fontSize = 10.sp, color = textMutedColor)
                        Text("$1,840.00", fontSize = 13.sp, fontWeight = FontWeight.Bold, color = textColor)
                    }
                    Column {
                        Text("Free Margin", fontSize = 10.sp, color = textMutedColor)
                        Text("$8,642.40", fontSize = 13.sp, fontWeight = FontWeight.Bold, color = textColor)
                    }
                    Column(horizontalAlignment = Alignment.End) {
                        Text("Win Rate", fontSize = 10.sp, color = textMutedColor)
                        Text("71.4%", fontSize = 13.sp, fontWeight = FontWeight.Bold, color = SemanticPositive)
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(14.dp))

        // Tabs
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            filterTabs.forEach { tab ->
                val isSelected = selectedTab.startsWith(tab.take(4))
                Surface(
                    shape = RoundedCornerShape(16.dp),
                    color = if (isSelected) BrandBlue else (if (isDark) DarkSurfaceRaised else LightSurfaceRaised),
                    border = BorderStroke(1.dp, if (isSelected) BrandBlue else borderColor),
                    modifier = Modifier.clickable { selectedTab = tab }
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

        Spacer(modifier = Modifier.height(14.dp))

        // Positions list
        LazyColumn(
            verticalArrangement = Arrangement.spacedBy(10.dp),
            modifier = Modifier.weight(1f)
        ) {
            items(positions, key = { it.id }) { pos ->
                val isLong = pos.direction == "LONG"
                val clean = pos.symbol.replace("/", "")
                val currentMark = livePrices[clean] ?: livePrices["${clean}USDT"] ?: pos.markPrice
                val pnlUsd = if (pos.entryPrice > 0) (currentMark - pos.entryPrice) * (pos.sizeUsd / pos.entryPrice) * (if (isLong) 1 else -1) else 0.0
                val pnlPct = if (pos.entryPrice > 0) ((currentMark - pos.entryPrice) / pos.entryPrice) * 100.0 * (if (isLong) 1 else -1) else 0.0
                val isPos = pnlUsd >= 0
                val pnlColor = if (isPos) SemanticPositive else SemanticNegative

                Surface(
                    shape = RoundedCornerShape(12.dp),
                    color = cardColor,
                    border = BorderStroke(1.dp, borderColor),
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable {
                            viewModel.openPositionDetail(pos.id)
                        }
                        .testTag("position_card_${pos.id}")
                ) {
                    Column(modifier = Modifier.padding(14.dp)) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Surface(
                                    shape = RoundedCornerShape(4.dp),
                                    color = if (isLong) (if (isDark) SemanticPositive.copy(alpha = 0.2f) else SemanticPositiveLight) else (if (isDark) SemanticNegative.copy(alpha = 0.2f) else SemanticNegativeLight)
                                ) {
                                    Text(
                                        text = "${pos.direction} ${pos.leverage}X",
                                        fontSize = 10.sp,
                                        fontWeight = FontWeight.Bold,
                                        color = if (isLong) SemanticPositive else SemanticNegative,
                                        modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                                    )
                                }
                                Spacer(modifier = Modifier.width(8.dp))
                                Text(
                                    text = pos.symbol,
                                    fontSize = 14.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = textColor
                                )
                            }

                            Text(
                                text = "${if (isPos) "+" else ""}$${String.format("%.2f", pnlUsd)} (${if (isPos) "+" else ""}${String.format("%.2f", pnlPct)}%)",
                                fontSize = 13.sp,
                                fontWeight = FontWeight.Bold,
                                color = pnlColor
                            )
                        }

                        Spacer(modifier = Modifier.height(10.dp))

                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Column {
                                Text("Size", fontSize = 10.sp, color = textMutedColor)
                                Text("$${String.format("%,.0f", pos.sizeUsd)}", fontSize = 12.sp, fontWeight = FontWeight.SemiBold, color = textColor)
                            }
                            Column {
                                Text("Entry", fontSize = 10.sp, color = textMutedColor)
                                Text("$${String.format("%,.1f", pos.entryPrice)}", fontSize = 12.sp, fontWeight = FontWeight.SemiBold, color = textColor)
                            }
                            Column {
                                Text("Mark", fontSize = 10.sp, color = textMutedColor)
                                Text("$${String.format("%,.1f", currentMark)}", fontSize = 12.sp, fontWeight = FontWeight.SemiBold, color = textColor)
                            }
                            Column(horizontalAlignment = Alignment.End) {
                                Text("Stop Loss", fontSize = 10.sp, color = textMutedColor)
                                Text("$${String.format("%,.1f", pos.stopLoss)}", fontSize = 12.sp, fontWeight = FontWeight.SemiBold, color = SemanticNegative)
                            }
                        }
                    }
                }
            }

            if (positions.isEmpty()) {
                item {
                    Surface(
                        shape = RoundedCornerShape(12.dp),
                        color = cardColor,
                        border = BorderStroke(1.dp, borderColor),
                        modifier = Modifier.fillMaxWidth().padding(vertical = 16.dp)
                    ) {
                        Column(
                            modifier = Modifier.padding(24.dp),
                            horizontalAlignment = Alignment.CenterHorizontally
                        ) {
                            Box(
                                modifier = Modifier
                                    .size(48.dp)
                                    .background(BrandBlue.copy(alpha = 0.15f), shape = RoundedCornerShape(12.dp)),
                                contentAlignment = Alignment.Center
                            ) {
                                Icon(Icons.Default.Add, contentDescription = null, tint = BrandBlue, modifier = Modifier.size(28.dp))
                            }
                            Spacer(modifier = Modifier.height(12.dp))
                            Text("No open simulation positions", fontSize = 15.sp, fontWeight = FontWeight.Bold, color = textColor)
                            Spacer(modifier = Modifier.height(6.dp))
                            Text("Open a risk-free paper trade directly from AI Prediction or the order ticket to simulate institutional trade execution.", fontSize = 12.sp, color = textMutedColor, textAlign = androidx.compose.ui.text.style.TextAlign.Center, lineHeight = 16.sp)
                            Spacer(modifier = Modifier.height(16.dp))
                            Button(
                                onClick = { viewModel.navigateTo(ScreenRoute.PAPER_ORDER_TICKET) },
                                colors = ButtonDefaults.buttonColors(containerColor = BrandBlue, contentColor = Color.White),
                                shape = RoundedCornerShape(8.dp),
                                modifier = Modifier.height(40.dp)
                            ) {
                                Text("OPEN SIMULATION ORDER", fontSize = 11.sp, fontWeight = FontWeight.Bold)
                            }
                        }
                    }
                }
            }

            item {
                Spacer(modifier = Modifier.height(10.dp))
                OutlinedButton(
                    onClick = { viewModel.resetPaperBalance() },
                    border = BorderStroke(1.dp, borderColor),
                    shape = RoundedCornerShape(10.dp),
                    modifier = Modifier.fillMaxWidth().height(44.dp)
                ) {
                    Icon(Icons.Default.Refresh, contentDescription = null, tint = BrandBlue, modifier = Modifier.size(16.dp))
                    Spacer(modifier = Modifier.width(6.dp))
                    Text("Reset simulation portfolio ($10,000)", fontSize = 12.sp, color = textMutedColor)
                }
                Spacer(modifier = Modifier.height(16.dp))
            }
        }
    }
}

