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
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.core.model.AssetSymbol
import com.example.ui.theme.*
import com.example.ui.viewmodel.AssetDetailTab
import com.example.ui.viewmodel.CryptoScopeViewModel
import com.example.ui.viewmodel.ScreenRoute

@Composable
fun NotificationsScreen(viewModel: CryptoScopeViewModel) {
    val uiState by viewModel.uiState.collectAsState()
    val isDark = uiState.isDarkTheme
    val bgColor = if (isDark) DarkBackground else LightBackground
    val cardColor = if (isDark) DarkSurface else LightSurface
    val borderColor = if (isDark) DarkBorder else LightBorder
    val textColor = if (isDark) DarkTextPrimary else LightTextPrimary
    val textMutedColor = if (isDark) DarkTextMuted else LightTextMuted

    val filterTabs = listOf("All", "Signals", "System", "Paper")
    var selectedTab by remember { mutableStateOf("All") }

    val notifications = listOf(
        Triple("BTC LONG • 1H Gated Alert", "Confidence 84 • Expected return +0.74% • Risk Low • 12m ago", "SIGNALS"),
        Triple("Data Feed Healthy", "Composite live sync: 0 dropped frames in last 4 hours • 1h ago", "SYSTEM"),
        Triple("Paper Order Filled", "BTC Long 0.15 BTC @ $109,420 • Margin $1,641.30 • 3h ago", "PAPER"),
        Triple("SOL Breakout Warning", "Order book bid skew reached +26% • 4h ago", "SIGNALS")
    )

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(bgColor)
            .padding(horizontal = 16.dp)
            .testTag("notifications_screen")
    ) {
        Spacer(modifier = Modifier.height(12.dp))

        // Header
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            IconButton(onClick = { viewModel.navigateBack() }, modifier = Modifier.size(32.dp)) {
                Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back", tint = textColor)
            }
            Spacer(modifier = Modifier.width(6.dp))
            Column {
                Text("Notifications", fontSize = 18.sp, fontWeight = FontWeight.Bold, color = textColor)
                Text("Feed & Alerts", fontSize = 10.sp, color = textMutedColor)
            }
        }

        Spacer(modifier = Modifier.height(12.dp))

        // Filter Pills
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            filterTabs.forEach { tab ->
                val isSelected = selectedTab == tab
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

        // Notification List
        LazyColumn(
            verticalArrangement = Arrangement.spacedBy(10.dp),
            modifier = Modifier.fillMaxSize()
        ) {
            items(notifications.filter { selectedTab == "All" || it.third.equals(selectedTab, ignoreCase = true) }) { (title, subtitle, type) ->
                Surface(
                    shape = RoundedCornerShape(12.dp),
                    color = cardColor,
                    border = BorderStroke(1.dp, borderColor),
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable {
                            if (type == "SIGNALS") {
                                viewModel.selectAsset(AssetSymbol.BTC)
                                viewModel.setAssetDetailTab(AssetDetailTab.OVERVIEW)
                                viewModel.navigateTo(ScreenRoute.ASSET_DETAIL)
                            } else if (type == "PAPER") {
                                viewModel.navigateTo(ScreenRoute.PAPER_DASHBOARD)
                            }
                        }
                ) {
                    Column(modifier = Modifier.padding(14.dp)) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(title, fontSize = 13.sp, fontWeight = FontWeight.Bold, color = textColor)
                            Surface(shape = RoundedCornerShape(4.dp), color = if (isDark) DarkSurfaceRaised else LightSurfaceRaised) {
                                Text(type, fontSize = 8.sp, fontWeight = FontWeight.Bold, color = BrandBlue, modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp))
                            }
                        }
                        Spacer(modifier = Modifier.height(4.dp))
                        Text(subtitle, fontSize = 11.sp, color = textMutedColor, lineHeight = 15.sp)
                    }
                }
            }
        }
    }
}

