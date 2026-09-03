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
import androidx.compose.material.icons.filled.CheckCircle
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
fun AlertsScreen(viewModel: CryptoScopeViewModel) {
    val uiState by viewModel.uiState.collectAsState()
    val isDark = uiState.isDarkTheme
    val bgColor = if (isDark) DarkBackground else LightBackground
    val cardColor = if (isDark) DarkSurface else LightSurface
    val borderColor = if (isDark) DarkBorder else LightBorder
    val textColor = if (isDark) DarkTextPrimary else LightTextPrimary
    val textMutedColor = if (isDark) DarkTextMuted else LightTextMuted

    val fallbackAlerts = listOf(
        Triple("alert-1", "BTC LONG • 1H", "Conf ≥ 80 • Agreement ≥ 75 • Quality ≥ 95 • Last checked 12s ago" to "ACTIVE"),
        Triple("alert-2", "SOL Breakout • 15M", "Conf ≥ 75 • Data quality ≥ 90 • Last checked 14s ago" to "ACTIVE"),
        Triple("alert-3", "ETH OI Spike • 1H", "OI > +5% 15m • Cooldown 60m • Last checked 14s ago" to "PAUSED")
    )

    val filterTabs = listOf("Active", "Triggered", "Paused")

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(bgColor)
            .padding(horizontal = 16.dp)
            .testTag("alerts_screen")
    ) {
        Spacer(modifier = Modifier.height(12.dp))

        // Top bar with CREATE button
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column {
                Text("Alerts", fontSize = 20.sp, fontWeight = FontWeight.Bold, color = textColor)
                Text("Confidence-gated notifications", fontSize = 11.sp, color = textMutedColor)
            }
            Button(
                onClick = { viewModel.navigateTo(ScreenRoute.CREATE_ALERT) },
                colors = ButtonDefaults.buttonColors(containerColor = BrandBlue, contentColor = Color.White),
                shape = RoundedCornerShape(8.dp),
                contentPadding = PaddingValues(horizontal = 12.dp, vertical = 6.dp),
                modifier = Modifier.height(36.dp).testTag("create_alert_cta")
            ) {
                Icon(Icons.Default.Add, contentDescription = null, modifier = Modifier.size(14.dp))
                Spacer(modifier = Modifier.width(4.dp))
                Text("CREATE", fontSize = 11.sp, fontWeight = FontWeight.Bold)
            }
        }

        Spacer(modifier = Modifier.height(12.dp))

        // Status Filter Tabs
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            filterTabs.forEach { tab ->
                val isSelected = uiState.selectedAlertFilterTab == tab
                Surface(
                    shape = RoundedCornerShape(16.dp),
                    color = if (isSelected) BrandBlue else (if (isDark) DarkSurfaceRaised else LightSurfaceRaised),
                    border = BorderStroke(1.dp, if (isSelected) BrandBlue else borderColor),
                    modifier = Modifier.clickable { viewModel.setAlertFilterTab(tab) }
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

        // Alerts List
        LazyColumn(
            verticalArrangement = Arrangement.spacedBy(10.dp),
            modifier = Modifier.weight(1f)
        ) {
            items(fallbackAlerts) { (id, title, details) ->
                val (desc, status) = details
                Surface(
                    shape = RoundedCornerShape(12.dp),
                    color = cardColor,
                    border = BorderStroke(1.dp, borderColor),
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable { viewModel.openAlertDetail(id) }
                        .testTag("alert_item_$id")
                ) {
                    Row(
                        modifier = Modifier.padding(14.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column(modifier = Modifier.weight(1f)) {
                            Text(title, fontSize = 13.sp, fontWeight = FontWeight.Bold, color = textColor)
                            Spacer(modifier = Modifier.height(4.dp))
                            Text(desc, fontSize = 10.sp, color = textMutedColor, lineHeight = 14.sp)
                        }
                        Spacer(modifier = Modifier.width(8.dp))
                        Surface(
                            shape = RoundedCornerShape(4.dp),
                            color = if (status == "ACTIVE") SemanticPositiveLight else (if (isDark) DarkSurfaceRaised else LightSurfaceRaised)
                        ) {
                            Text(
                                text = status,
                                fontSize = 9.sp,
                                fontWeight = FontWeight.Bold,
                                color = if (status == "ACTIVE") SemanticPositive else textMutedColor,
                                modifier = Modifier.padding(horizontal = 8.dp, vertical = 3.dp)
                            )
                        }
                    }
                }
            }

            item {
                Spacer(modifier = Modifier.height(6.dp))
                Text("Alert Quality", fontSize = 13.sp, fontWeight = FontWeight.Bold, color = textColor)
            }

            item {
                // Quality Stats Box
                Surface(
                    shape = RoundedCornerShape(12.dp),
                    color = cardColor,
                    border = BorderStroke(1.dp, borderColor),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Row(
                        modifier = Modifier.padding(14.dp),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Column {
                            Text("Triggered 30d", fontSize = 10.sp, color = textMutedColor)
                            Text("18", fontSize = 16.sp, fontWeight = FontWeight.Bold, color = textColor)
                            Text("5/w avg", fontSize = 9.sp, color = textMutedColor)
                        }
                        Column {
                            Text("Precision", fontSize = 10.sp, color = textMutedColor)
                            Text("72%", fontSize = 16.sp, fontWeight = FontWeight.Bold, color = SemanticPositive)
                            Text("Defined criteria", fontSize = 9.sp, color = textMutedColor)
                        }
                        Column {
                            Text("Spam blocked", fontSize = 10.sp, color = textMutedColor)
                            Text("41", fontSize = 16.sp, fontWeight = FontWeight.Bold, color = BrandGold)
                            Text("Cooldown", fontSize = 9.sp, color = textMutedColor)
                        }
                    }
                }
            }

            item {
                // Gating Rules Explanation Box
                Surface(
                    shape = RoundedCornerShape(12.dp),
                    color = cardColor,
                    border = BorderStroke(1.dp, borderColor),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(modifier = Modifier.padding(14.dp)) {
                        Text("Signals only notify when:", fontSize = 11.sp, fontWeight = FontWeight.Bold, color = textColor)
                        Spacer(modifier = Modifier.height(8.dp))
                        GatingCheckRow("Confidence threshold passes (≥ 75%)", textMutedColor)
                        GatingCheckRow("Model agreement passes (≥ 70%)", textMutedColor)
                        GatingCheckRow("Data quality healthy (≥ 90%)", textMutedColor)
                        GatingCheckRow("Expected edge > trading costs", textMutedColor)
                        GatingCheckRow("Risk engine ALLOW state active", textMutedColor)
                    }
                }
                Spacer(modifier = Modifier.height(16.dp))
            }
        }
    }
}

@Composable
private fun GatingCheckRow(text: String, textMutedColor: Color) {
    Row(
        modifier = Modifier.padding(vertical = 2.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(Icons.Default.CheckCircle, contentDescription = null, tint = SemanticPositive, modifier = Modifier.size(12.dp))
        Spacer(modifier = Modifier.width(6.dp))
        Text(text, fontSize = 10.sp, color = textMutedColor)
    }
}

