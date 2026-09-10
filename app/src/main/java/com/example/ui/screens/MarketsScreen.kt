package com.example.ui.screens

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.FilterList
import androidx.compose.material.icons.filled.Search
import androidx.compose.material.icons.filled.Star
import androidx.compose.material.icons.filled.StarBorder
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
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
fun MarketsScreen(viewModel: CryptoScopeViewModel) {
    val uiState by viewModel.uiState.collectAsState()
    val isDark = uiState.isDarkTheme
    val bgColor = if (isDark) DarkBackground else LightBackground
    val cardColor = if (isDark) DarkSurface else LightSurface
    val borderColor = if (isDark) DarkBorder else LightBorder
    val textColor = if (isDark) DarkTextPrimary else LightTextPrimary
    val textMutedColor = if (isDark) DarkTextMuted else LightTextMuted

    val liveMarkets by viewModel.liveMarkets.collectAsState()

    var topTab by remember { mutableStateOf("Derivatives") }
    var subTab by remember { mutableStateOf("Markets") }
    var searchQuery by remember { mutableStateOf("") }
    var sortByChange by remember { mutableStateOf(false) }

    val filteredMarkets = remember(liveMarkets, searchQuery, subTab, sortByChange, uiState.watchlist) {
        val base = when (subTab) {
            "Favorites" -> liveMarkets.filter { uiState.watchlist.contains(it.asset) }
            "Category" -> liveMarkets.filter { it.asset in setOf("BTC", "ETH", "SOL", "BNB") }
            else -> liveMarkets
        }
        base.filter {
            if (searchQuery.isBlank()) true
            else it.asset.contains(searchQuery, ignoreCase = true) || it.pair.contains(searchQuery, ignoreCase = true)
        }.let { list ->
            if (sortByChange) list.sortedByDescending { it.change24h }
            else list
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(bgColor)
            .testTag("markets_screen")
    ) {
        // Top Main Tabs (Derivatives, Spot, Hyperliquid)
        Surface(
            color = cardColor,
            border = BorderStroke(0.5.dp, borderColor),
            modifier = Modifier.fillMaxWidth()
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 10.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(horizontalArrangement = Arrangement.spacedBy(18.dp)) {
                    listOf("Derivatives", "Spot", "Hyperliquid").forEach { tab ->
                        val selected = topTab == tab
                        Column(
                            modifier = Modifier.clickable { topTab = tab },
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
                                        .width(22.dp)
                                        .height(3.dp)
                                        .clip(CircleShape)
                                        .background(BrandBlue)
                                )
                            }
                        }
                    }
                }

                Row(verticalAlignment = Alignment.CenterVertically) {
                    IconButton(
                        onClick = { viewModel.navigateTo(ScreenRoute.WATCHLIST) },
                        modifier = Modifier.size(36.dp)
                    ) {
                        Icon(
                            imageVector = Icons.Default.Star,
                            contentDescription = "Watchlist Screen",
                            tint = BrandGold,
                            modifier = Modifier.size(20.dp)
                        )
                    }
                    IconButton(
                        onClick = { viewModel.navigateTo(ScreenRoute.GLOBAL_SEARCH) },
                        modifier = Modifier.size(36.dp)
                    ) {
                        Icon(
                            imageVector = Icons.Default.Search,
                            contentDescription = "Search",
                            tint = textColor,
                            modifier = Modifier.size(20.dp)
                        )
                    }
                }
            }
        }

        // Subtabs (Favorites, Markets, Category, Token Unlocks, Customize, Filter)
        Surface(
            color = cardColor,
            border = BorderStroke(0.5.dp, borderColor),
            modifier = Modifier.fillMaxWidth()
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 12.dp, vertical = 8.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                LazyRow(
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    modifier = Modifier.weight(1f)
                ) {
                    val subTabs = listOf("Favorites", "Markets", "Category", "Token Unlocks", "Customize")
                    items(subTabs) { tab ->
                        val isSelected = subTab == tab
                        Surface(
                            shape = RoundedCornerShape(14.dp),
                            color = if (isSelected) (if (isDark) DarkSurfaceRaised else LightSurfaceRaised) else Color.Transparent,
                            modifier = Modifier.clickable { subTab = tab }
                        ) {
                            Text(
                                text = tab,
                                fontSize = 12.sp,
                                fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Normal,
                                color = if (isSelected) BrandBlue else textMutedColor,
                                modifier = Modifier.padding(horizontal = 10.dp, vertical = 5.dp)
                            )
                        }
                    }
                }

                IconButton(onClick = { sortByChange = !sortByChange }, modifier = Modifier.size(30.dp)) {
                    Icon(Icons.Default.FilterList, contentDescription = "Filter", tint = textMutedColor, modifier = Modifier.size(18.dp))
                }
            }
        }

        // Table Header
        Surface(
            color = if (isDark) DarkSurfaceRaised else LightSurfaceRaised,
            modifier = Modifier.fillMaxWidth()
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 8.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text("Coin / Vol", fontSize = 11.sp, color = textMutedColor, modifier = Modifier.weight(1.3f))
                Text("7D Trend", fontSize = 11.sp, color = textMutedColor, modifier = Modifier.weight(1f))
                Text("Price ⇅", fontSize = 11.sp, color = textMutedColor, modifier = Modifier.weight(1.2f))
                Text("24H Chg ⇅", fontSize = 11.sp, color = textMutedColor, modifier = Modifier.weight(1f))
            }
        }

        // Market Coin List
        LazyColumn(
            modifier = Modifier.fillMaxSize(),
            contentPadding = PaddingValues(bottom = 80.dp)
        ) {
            items(filteredMarkets) { market ->
                val isPositive = market.change24h >= 0
                val badgeColor = if (isPositive) SemanticPositive else SemanticNegative

                Surface(
                    color = cardColor,
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable {
                            val asset = try {
                                AssetSymbol.valueOf(market.asset)
                            } catch (e: Exception) {
                                AssetSymbol.BTC
                            }
                            viewModel.selectAsset(asset)
                            viewModel.setAssetDetailTab(AssetDetailTab.SPOT)
                            viewModel.navigateTo(ScreenRoute.ASSET_DETAIL)
                        }
                ) {
                    Column {
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(horizontal = 16.dp, vertical = 12.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            // Coin info
                            Row(
                                modifier = Modifier.weight(1.4f),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                val isFav = uiState.watchlist.contains(market.asset)
                                IconButton(
                                    onClick = { viewModel.toggleWatchlist(market.asset) },
                                    modifier = Modifier.size(24.dp).testTag("fav_btn_${market.asset}")
                                ) {
                                    Icon(
                                        imageVector = if (isFav) Icons.Default.Star else Icons.Default.StarBorder,
                                        contentDescription = "Favorite",
                                        tint = if (isFav) BrandGold else textMutedColor.copy(alpha = 0.5f),
                                        modifier = Modifier.size(15.dp)
                                    )
                                }
                                Spacer(modifier = Modifier.width(4.dp))
                                Box(
                                    modifier = Modifier
                                        .size(28.dp)
                                        .clip(CircleShape)
                                        .background(if (market.asset == "BTC") BrandGold.copy(alpha = 0.15f) else BrandBlue.copy(alpha = 0.15f)),
                                    contentAlignment = Alignment.Center
                                ) {
                                    Text(
                                        text = market.asset.take(1),
                                        fontSize = 12.sp,
                                        fontWeight = FontWeight.Bold,
                                        color = if (market.asset == "BTC") BrandGold else BrandBlue
                                    )
                                }
                                Spacer(modifier = Modifier.width(6.dp))
                                Column {
                                    Text(
                                        text = market.asset,
                                        fontSize = 14.sp,
                                        fontWeight = FontWeight.Bold,
                                        color = textColor
                                    )
                                    Text(
                                        text = "Vol $${String.format("%.1f", market.volume24h / 1e9)}B",
                                        fontSize = 10.sp,
                                        color = textMutedColor
                                    )
                                }
                            }

                            // 7D Sparkline Canvas
                            Box(
                                modifier = Modifier
                                    .weight(1f)
                                    .height(28.dp)
                                    .padding(horizontal = 4.dp)
                            ) {
                                Canvas(modifier = Modifier.fillMaxSize()) {
                                    val w = size.width
                                    val h = size.height
                                    val path = Path().apply {
                                        moveTo(0f, if (isPositive) h * 0.8f else h * 0.2f)
                                        lineTo(w * 0.25f, if (isPositive) h * 0.6f else h * 0.4f)
                                        lineTo(w * 0.5f, if (isPositive) h * 0.7f else h * 0.3f)
                                        lineTo(w * 0.75f, if (isPositive) h * 0.3f else h * 0.7f)
                                        lineTo(w, if (isPositive) h * 0.15f else h * 0.85f)
                                    }
                                    drawPath(
                                        path = path,
                                        color = badgeColor,
                                        style = Stroke(width = 1.8.dp.toPx(), cap = StrokeCap.Round)
                                    )
                                }
                            }

                            // Price
                            Column(
                                modifier = Modifier.weight(1.2f),
                                horizontalAlignment = Alignment.Start
                            ) {
                                val formattedPrice = when {
                                    market.price >= 100 -> String.format(java.util.Locale.US, "%,.2f", market.price)
                                    market.price >= 1 -> String.format(java.util.Locale.US, "%.3f", market.price)
                                    else -> String.format(java.util.Locale.US, "%.4f", market.price)
                                }
                                Text(
                                    text = "$$formattedPrice",
                                    fontSize = 14.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = textColor
                                )
                                val mcapDisplay = when (market.asset) {
                                    "BTC" -> "$${String.format(java.util.Locale.US, "%.2f", (market.price * 19.8e6) / 1e12)}T"
                                    "ETH" -> "$${String.format(java.util.Locale.US, "%.1f", (market.price * 120.4e6) / 1e9)}B"
                                    "SOL" -> "$${String.format(java.util.Locale.US, "%.1f", (market.price * 470e6) / 1e9)}B"
                                    "BNB" -> "$${String.format(java.util.Locale.US, "%.1f", (market.price * 145e6) / 1e9)}B"
                                    "XRP" -> "$${String.format(java.util.Locale.US, "%.1f", (market.price * 57e9) / 1e9)}B"
                                    "DOGE" -> "$${String.format(java.util.Locale.US, "%.1f", (market.price * 148e9) / 1e9)}B"
                                    "AVAX" -> "$${String.format(java.util.Locale.US, "%.1f", (market.price * 400e6) / 1e9)}B"
                                    "SUI" -> "$${String.format(java.util.Locale.US, "%.1f", (market.price * 2.8e9) / 1e9)}B"
                                    "LINK" -> "$${String.format(java.util.Locale.US, "%.1f", (market.price * 608e6) / 1e9)}B"
                                    "ADA" -> "$${String.format(java.util.Locale.US, "%.1f", (market.price * 35.7e9) / 1e9)}B"
                                    else -> "$${String.format(java.util.Locale.US, "%.1f", (market.volume24h * 5) / 1e9)}B"
                                }
                                Text(
                                    text = "MCap: $mcapDisplay",
                                    fontSize = 10.sp,
                                    color = textMutedColor
                                )
                            }

                            // 24H Chg Badge
                            Surface(
                                shape = RoundedCornerShape(6.dp),
                                color = badgeColor,
                                modifier = Modifier.weight(1f)
                            ) {
                                Text(
                                    text = "${if (isPositive) "+" else ""}${String.format(java.util.Locale.US, "%.2f", market.change24h)}%",
                                    fontSize = 12.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = Color.White,
                                    modifier = Modifier
                                        .padding(horizontal = 6.dp, vertical = 4.dp)
                                        .wrapContentWidth(Alignment.CenterHorizontally)
                                )
                            }
                        }

                        HorizontalDivider(color = borderColor, thickness = 0.5.dp)
                    }
                }
            }

            if (filteredMarkets.isEmpty()) {
                item {
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(top = 60.dp, start = 32.dp, end = 32.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Icon(
                                imageVector = if (subTab == "Favorites") Icons.Default.StarBorder else Icons.Default.Search,
                                contentDescription = null,
                                tint = textMutedColor,
                                modifier = Modifier.size(48.dp)
                            )
                            Spacer(modifier = Modifier.height(14.dp))
                            Text(
                                text = if (subTab == "Favorites") "No favorites saved yet" else "No matching crypto pairs",
                                fontSize = 16.sp,
                                fontWeight = FontWeight.Bold,
                                color = textColor
                            )
                            Spacer(modifier = Modifier.height(6.dp))
                            Text(
                                text = if (subTab == "Favorites") 
                                    "Tap the star icon next to any coin in the Markets tab to monitor it in your favorites."
                                else 
                                    "Try adjusting your search query or filter criteria.",
                                fontSize = 12.sp,
                                color = textMutedColor,
                                textAlign = androidx.compose.ui.text.style.TextAlign.Center,
                                lineHeight = 16.sp
                            )
                        }
                    }
                }
            }
        }
    }
}
