package com.example.ui.screens

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
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
import com.example.ui.components.Sparkline
import com.example.ui.theme.*
import com.example.ui.viewmodel.CryptoScopeViewModel

@Composable
fun OnChainScreen(viewModel: CryptoScopeViewModel) {
    val uiState by viewModel.uiState.collectAsState()
    val isDark = uiState.isDarkTheme
    val bgColor = if (isDark) DarkBackground else LightBackground
    val cardColor = if (isDark) DarkSurface else LightSurface
    val borderColor = if (isDark) DarkBorder else LightBorder
    val textColor = if (isDark) DarkTextPrimary else LightTextPrimary
    val textMutedColor = if (isDark) DarkTextMuted else LightTextMuted

    val onchain = remember(uiState.selectedAsset) {
        viewModel.repository.getOnChain(uiState.selectedAsset)
    }

    var selectedTab by remember { mutableStateOf("Overview") }
    val tabs = listOf("Overview", "Flows", "Whales", "Network")

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(bgColor)
            .padding(horizontal = 16.dp)
            .verticalScroll(rememberScrollState())
            .testTag("onchain_screen")
    ) {
        Spacer(modifier = Modifier.height(12.dp))

        // Sub Tabs
        Row(
            modifier = Modifier.fillMaxWidth().padding(bottom = 12.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            tabs.forEach { tab ->
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

        // 2x2 Grid of Onchain Metrics
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
                    Text("Exchange Netflow", fontSize = 10.sp, color = textMutedColor)
                    Spacer(modifier = Modifier.height(4.dp))
                    Text("${onchain.exchangeNetflowBtc / 1000}K ${onchain.asset}", fontSize = 15.sp, fontWeight = FontWeight.Bold, color = SemanticPositive)
                    Text("Outflow dominant", fontSize = 9.sp, color = SemanticPositive)
                }
            }

            Surface(
                shape = RoundedCornerShape(12.dp),
                color = cardColor,
                border = BorderStroke(1.dp, borderColor),
                modifier = Modifier.weight(1f)
            ) {
                Column(modifier = Modifier.padding(12.dp)) {
                    Text("Whale deposits", fontSize = 10.sp, color = textMutedColor)
                    Spacer(modifier = Modifier.height(4.dp))
                    Text("Low", fontSize = 15.sp, fontWeight = FontWeight.Bold, color = SemanticPositive)
                    Text("22% below 30d avg", fontSize = 9.sp, color = textMutedColor)
                }
            }
        }

        Spacer(modifier = Modifier.height(10.dp))

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
                    Text("SOPR", fontSize = 10.sp, color = textMutedColor)
                    Spacer(modifier = Modifier.height(4.dp))
                    Text("${onchain.sopr}", fontSize = 15.sp, fontWeight = FontWeight.Bold, color = textColor)
                    Text("Mid-gain selling", fontSize = 9.sp, color = textMutedColor)
                }
            }

            Surface(
                shape = RoundedCornerShape(12.dp),
                color = cardColor,
                border = BorderStroke(1.dp, borderColor),
                modifier = Modifier.weight(1f)
            ) {
                Column(modifier = Modifier.padding(12.dp)) {
                    Text("MVRV", fontSize = 10.sp, color = textMutedColor)
                    Spacer(modifier = Modifier.height(4.dp))
                    Text("${onchain.mvrv}", fontSize = 15.sp, fontWeight = FontWeight.Bold, color = BrandBlue)
                    Text("Moderate value zone", fontSize = 9.sp, color = BrandBlue)
                }
            }
        }

        Spacer(modifier = Modifier.height(10.dp))

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
                    Text("Hash rate", fontSize = 10.sp, color = textMutedColor)
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(onchain.hashRate, fontSize = 15.sp, fontWeight = FontWeight.Bold, color = textColor)
                }
            }

            Surface(
                shape = RoundedCornerShape(12.dp),
                color = cardColor,
                border = BorderStroke(1.dp, borderColor),
                modifier = Modifier.weight(1f)
            ) {
                Column(modifier = Modifier.padding(12.dp)) {
                    Text("Active addresses", fontSize = 10.sp, color = textMutedColor)
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(onchain.activeAddresses, fontSize = 15.sp, fontWeight = FontWeight.Bold, color = SemanticPositive)
                }
            }
        }

        Spacer(modifier = Modifier.height(14.dp))

        // Exchange flow trend
        Surface(
            shape = RoundedCornerShape(14.dp),
            color = cardColor,
            border = BorderStroke(1.dp, borderColor),
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(modifier = Modifier.padding(14.dp)) {
                Text("Exchange flow trend (7d)", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = textColor)
                Spacer(modifier = Modifier.height(12.dp))
                Sparkline(
                    data = onchain.trend,
                    modifier = Modifier.fillMaxWidth().height(70.dp),
                    isPositive = true
                )
            }
        }

        Spacer(modifier = Modifier.height(14.dp))

        // AI interpretation Card
        Surface(
            shape = RoundedCornerShape(14.dp),
            color = cardColor,
            border = BorderStroke(1.dp, borderColor),
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(modifier = Modifier.padding(14.dp)) {
                Text("AI interpretation", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = textColor)
                Spacer(modifier = Modifier.height(6.dp))
                Text("Constructive on-chain backdrop", fontSize = 13.sp, fontWeight = FontWeight.Bold, color = SemanticPositive)
                Spacer(modifier = Modifier.height(8.dp))
                onchain.takeaways.forEach { takeaway ->
                    Text("• $takeaway", fontSize = 11.sp, color = textMutedColor, lineHeight = 16.sp)
                    Spacer(modifier = Modifier.height(4.dp))
                }
            }
        }

        Spacer(modifier = Modifier.height(60.dp))
    }
}

