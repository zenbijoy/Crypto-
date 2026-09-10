package com.example.ui.screens

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Notifications
import androidx.compose.material.icons.filled.Share
import androidx.compose.material.icons.filled.Warning
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
import com.example.ui.theme.*
import com.example.ui.viewmodel.CryptoScopeViewModel
import com.example.ui.viewmodel.ScreenRoute

data class NewsItem(
    val id: String,
    val title: String,
    val content: String,
    val timeAgo: String,
    val category: String,
    val isAlert: Boolean = false,
    val source: String = "CryptoScope AI"
)

@Composable
fun NewsScreen(viewModel: CryptoScopeViewModel) {
    val uiState by viewModel.uiState.collectAsState()
    val isDark = uiState.isDarkTheme
    val bgColor = if (isDark) DarkBackground else LightBackground
    val cardColor = if (isDark) DarkSurface else LightSurface
    val borderColor = if (isDark) DarkBorder else LightBorder
    val textColor = if (isDark) DarkTextPrimary else LightTextPrimary
    val textMutedColor = if (isDark) DarkTextMuted else LightTextMuted

    var activeTab by remember { mutableStateOf("News flash") }
    var selectedFilter by remember { mutableStateOf("All") }

    val backendNews by viewModel.repository.backendNews.collectAsState()
    val radarAlerts by viewModel.repository.contractRadarAlerts.collectAsState()

    val newsItems = remember(backendNews, radarAlerts, activeTab) {
        if (activeTab == "News flash") {
            val alertItems = radarAlerts.map { alert ->
                NewsItem(
                    id = "radar_${alert.symbol}_${alert.riskScore}",
                    title = "${alert.asset} ${alert.triggerReason.ifEmpty { "High Risk Alert" }}",
                    content = "${alert.symbol} dominant side: ${alert.dominantSide}. Liquidation pool at $${String.format(java.util.Locale.US, "%,.2f", alert.liquidationPoolPrice)} (${String.format(java.util.Locale.US, "%.1f", alert.distancePct)}% distance). OI Surge: +${String.format(java.util.Locale.US, "%.1f", alert.oiSurge24hPct)}%.",
                    timeAgo = "10m ago",
                    category = "Radar",
                    isAlert = alert.severity == "HIGH" || alert.severity == "CRITICAL",
                    source = "Contract Radar"
                )
            }
            val flashItems = backendNews.map {
                NewsItem(
                    id = it.id,
                    title = it.title,
                    content = it.summary,
                    timeAgo = it.publishedAt.ifEmpty { "Just now" },
                    category = it.category.ifEmpty { "News" },
                    isAlert = it.sentiment.contains("bear", ignoreCase = true) || it.sentimentScore < -0.2,
                    source = it.source.ifEmpty { "Cointelegraph" }
                )
            }
            val combined = alertItems + flashItems
            if (combined.isNotEmpty()) combined else listOf(
                NewsItem(
                    id = "1",
                    title = "ETH Large 【long】 Liquidation",
                    content = "Binance-ETHUSDT experienced a large 【long】 Liquidation, order TradeTurnover is 【$11.99M】, order price 【$2,423.17】.",
                    timeAgo = "1 hour ago",
                    category = "Liquidation",
                    isAlert = true
                ),
                NewsItem(
                    id = "2",
                    title = "In the last 4 hours, the main liquidation Long orders",
                    content = "In the past 4 hours, a total of 14,469 accounts were liquidated across Binance, Bybit, and OKX, with a total liquidation amount of $49.77M. The largest single liquidation occurred on Binance-BTCUSDT valued at $4.18M.",
                    timeAgo = "2 hours ago",
                    category = "Liquidation",
                    isAlert = true
                )
            )
        } else {
            val articles = backendNews.map {
                NewsItem(
                    id = it.id,
                    title = it.title,
                    content = it.summary,
                    timeAgo = it.publishedAt.ifEmpty { "Recently" },
                    category = it.category.ifEmpty { "General" },
                    isAlert = false,
                    source = it.source.ifEmpty { "CryptoScope Feed" }
                )
            }
            if (articles.isNotEmpty()) articles else listOf(
                NewsItem(
                    id = "3",
                    title = "Bitcoin Aggregate Open Interest Surges",
                    content = "Aggregate Bitcoin open interest across major derivatives exchanges reached record highs today as funding rates stay positive and institutional inflows continue.",
                    timeAgo = "3 hours ago",
                    category = "Derivatives"
                ),
                NewsItem(
                    id = "4",
                    title = "Spot Bitcoin ETF Net Daily Inflows Positive",
                    content = "US Spot Bitcoin ETFs registered net positive inflows continuing an ongoing weekly accumulation streak.",
                    timeAgo = "5 hours ago",
                    category = "ETF"
                )
            )
        }
    }

    val filteredItems = remember(newsItems, selectedFilter) {
        if (selectedFilter == "All") newsItems
        else newsItems.filter { it.category.equals(selectedFilter, ignoreCase = true) }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(bgColor)
            .testTag("news_screen")
    ) {
        // Top Header Tabs (News Flash vs News)
        Surface(
            color = cardColor,
            border = BorderStroke(0.5.dp, borderColor),
            modifier = Modifier.fillMaxWidth()
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 12.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(horizontalArrangement = Arrangement.spacedBy(20.dp)) {
                    listOf("News flash", "News").forEach { tab ->
                        val selected = activeTab == tab
                        Column(
                            modifier = Modifier.clickable { activeTab = tab },
                            horizontalAlignment = Alignment.CenterHorizontally
                        ) {
                            Text(
                                text = tab,
                                fontSize = 16.sp,
                                fontWeight = if (selected) FontWeight.Bold else FontWeight.Normal,
                                color = if (selected) textColor else textMutedColor
                            )
                            if (selected) {
                                Spacer(modifier = Modifier.height(4.dp))
                                Box(
                                    modifier = Modifier
                                        .width(24.dp)
                                        .height(3.dp)
                                        .clip(CircleShape)
                                        .background(BrandBlue)
                                )
                            }
                        }
                    }
                }

                IconButton(
                    onClick = { viewModel.navigateTo(ScreenRoute.NOTIFICATIONS) },
                    modifier = Modifier.size(36.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.Notifications,
                        contentDescription = "Notifications",
                        tint = textColor,
                        modifier = Modifier.size(20.dp)
                    )
                }
            }
        }

        // Category Filter Chips
        LazyRow(
            contentPadding = PaddingValues(horizontal = 16.dp, vertical = 10.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            val filters = listOf("All", "Liquidation", "Whale Alert", "Derivatives", "ETF")
            items(filters) { filter ->
                val selected = selectedFilter == filter
                Surface(
                    shape = RoundedCornerShape(16.dp),
                    color = if (selected) BrandBlue else cardColor,
                    border = BorderStroke(1.dp, if (selected) BrandBlue else borderColor),
                    modifier = Modifier.clickable { selectedFilter = filter }
                ) {
                    Text(
                        text = filter,
                        fontSize = 12.sp,
                        fontWeight = if (selected) FontWeight.Bold else FontWeight.Normal,
                        color = if (selected) Color.White else textMutedColor,
                        modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp)
                    )
                }
            }
        }

        // News Timeline Feed
        LazyColumn(
            modifier = Modifier.fillMaxSize(),
            contentPadding = PaddingValues(start = 16.dp, end = 16.dp, bottom = 80.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            items(filteredItems) { item ->
                Surface(
                    shape = RoundedCornerShape(14.dp),
                    color = cardColor,
                    border = BorderStroke(1.dp, borderColor),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(modifier = Modifier.padding(14.dp)) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                if (item.isAlert) {
                                    Box(
                                        modifier = Modifier
                                            .size(8.dp)
                                            .clip(CircleShape)
                                            .background(SemanticNegative)
                                    )
                                    Spacer(modifier = Modifier.width(6.dp))
                                }
                                Text(
                                    text = item.timeAgo,
                                    fontSize = 11.sp,
                                    color = textMutedColor
                                )
                            }

                            Surface(
                                shape = RoundedCornerShape(4.dp),
                                color = if (item.isAlert) SemanticNegativeLight else BrandBlueLight
                            ) {
                                Text(
                                    text = item.category,
                                    fontSize = 10.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = if (item.isAlert) SemanticNegative else BrandBlue,
                                    modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                                )
                            }
                        }

                        Spacer(modifier = Modifier.height(8.dp))

                        Text(
                            text = item.title,
                            fontSize = 14.sp,
                            fontWeight = FontWeight.Bold,
                            color = textColor
                        )

                        Spacer(modifier = Modifier.height(6.dp))

                        Text(
                            text = item.content,
                            fontSize = 12.sp,
                            color = textMutedColor,
                            lineHeight = 18.sp
                        )

                        Spacer(modifier = Modifier.height(10.dp))

                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(
                                text = "Source: ${item.source}",
                                fontSize = 10.sp,
                                color = textMutedColor
                            )

                            Icon(
                                imageVector = Icons.Default.Share,
                                contentDescription = "Share",
                                tint = textMutedColor,
                                modifier = Modifier
                                    .size(16.dp)
                                    .clickable { /* Share */ }
                            )
                        }
                    }
                }
            }
        }
    }
}
