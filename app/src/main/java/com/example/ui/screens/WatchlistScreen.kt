package com.example.ui.screens

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.scaleIn
import androidx.compose.animation.scaleOut
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.gestures.detectDragGestures
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.IntOffset
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.core.model.AssetSymbol
import com.example.ui.theme.*
import com.example.ui.viewmodel.AssetDetailTab
import com.example.ui.viewmodel.CryptoScopeViewModel
import com.example.ui.viewmodel.MainTab
import com.example.ui.viewmodel.ScreenRoute
import kotlin.math.roundToInt

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun WatchlistScreen(viewModel: CryptoScopeViewModel) {
    val uiState by viewModel.uiState.collectAsState()
    val isDark = uiState.isDarkTheme
    val bgColor = if (isDark) DarkBackground else LightBackground
    val cardColor = if (isDark) DarkSurface else LightSurface
    val borderColor = if (isDark) DarkBorder else LightBorder
    val textColor = if (isDark) DarkTextPrimary else LightTextPrimary
    val textMutedColor = if (isDark) DarkTextMuted else LightTextMuted

    val livePrices by viewModel.repository.livePrices.collectAsState()
    val allMarkets = remember(livePrices) { viewModel.repository.getMarkets() }

    val categories = listOf("All Pinned", "Layer 1", "DeFi / Meta")
    var selectedCategory by remember { mutableStateOf("All Pinned") }

    // Filter pinned markets from Room watchlist
    val pinnedMarkets = remember(allMarkets, uiState.watchlist, selectedCategory) {
        val inWatchlist = allMarkets.filter { uiState.watchlist.contains(it.asset) }
        when (selectedCategory) {
            "Layer 1" -> inWatchlist.filter { it.asset in setOf("BTC", "ETH", "SOL", "BNB", "AVAX") }
            "DeFi / Meta" -> inWatchlist.filter { it.asset in setOf("LINK", "UNI", "AAVE", "DOGE") }
            else -> inWatchlist
        }
    }

    // Draggable floating price icon coordinates
    var offsetX by remember { mutableFloatStateOf(0f) }
    var offsetY by remember { mutableFloatStateOf(0f) }

    // Resolve current selected floating price asset data
    val floatingSymbol = uiState.floatingPriceAsset
    val floatingMarket = allMarkets.find { it.asset == floatingSymbol }
        ?: allMarkets.firstOrNull()

    val floatingPrice = floatingMarket?.price
        ?: livePrices[floatingSymbol]
        ?: livePrices["${floatingSymbol}USDT"]
        ?: 0.0
    val floatingChange = floatingMarket?.change24h ?: 0.0
    val isFloatingPos = floatingChange >= 0

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text(
                            text = "Watchlist & Pinned Assets",
                            fontSize = 17.sp,
                            fontWeight = FontWeight.Bold,
                            color = textColor
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Surface(
                            shape = CircleShape,
                            color = BrandBlueLight
                        ) {
                            Text(
                                text = "${pinnedMarkets.size}",
                                fontSize = 11.sp,
                                fontWeight = FontWeight.Bold,
                                color = BrandBlue,
                                modifier = Modifier.padding(horizontal = 7.dp, vertical = 2.dp)
                            )
                        }
                    }
                },
                navigationIcon = {
                    IconButton(
                        onClick = {
                            if (!viewModel.navigateBack()) {
                                viewModel.navigateTo(ScreenRoute.MAIN)
                            }
                        },
                        modifier = Modifier.testTag("watchlist_back_button")
                    ) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = "Back",
                            tint = textColor
                        )
                    }
                },
                actions = {
                    // Toggle floating price overlay
                    IconButton(
                        onClick = { viewModel.toggleFloatingPriceVisible() },
                        modifier = Modifier.testTag("toggle_floating_icon_button")
                    ) {
                        Icon(
                            imageVector = if (uiState.isFloatingPriceVisible) Icons.Default.Visibility else Icons.Default.VisibilityOff,
                            contentDescription = "Toggle Floating Price Icon",
                            tint = if (uiState.isFloatingPriceVisible) BrandGold else textMutedColor
                        )
                    }
                    // Search to add more assets
                    IconButton(
                        onClick = { viewModel.navigateTo(ScreenRoute.GLOBAL_SEARCH) },
                        modifier = Modifier.testTag("watchlist_search_button")
                    ) {
                        Icon(
                            imageVector = Icons.Default.Search,
                            contentDescription = "Search Assets",
                            tint = textColor
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = cardColor)
            )
        },
        floatingActionButton = {
            FloatingActionButton(
                onClick = { viewModel.navigateTo(ScreenRoute.GLOBAL_SEARCH) },
                containerColor = BrandGold,
                contentColor = BackgroundDark,
                shape = RoundedCornerShape(16.dp),
                modifier = Modifier
                    .testTag("watchlist_add_fab")
                    .padding(bottom = 12.dp)
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    modifier = Modifier.padding(horizontal = 14.dp)
                ) {
                    Icon(Icons.Default.Add, contentDescription = "Add Coin", modifier = Modifier.size(18.dp))
                    Spacer(modifier = Modifier.width(6.dp))
                    Text("Pin Asset", fontSize = 13.sp, fontWeight = FontWeight.Bold)
                }
            }
        },
        containerColor = bgColor
    ) { paddingValues ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .background(bgColor)
                .testTag("watchlist_screen")
        ) {
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(horizontal = 16.dp),
                contentPadding = PaddingValues(top = 12.dp, bottom = 96.dp),
                verticalArrangement = Arrangement.spacedBy(10.dp)
            ) {
                // Category Pills + Live Stream Indicator
                item {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            categories.forEach { cat ->
                                val isSelected = selectedCategory == cat
                                Surface(
                                    shape = RoundedCornerShape(16.dp),
                                    color = if (isSelected) BrandBlueLight else cardColor,
                                    border = BorderStroke(1.dp, if (isSelected) BrandBlue else borderColor),
                                    modifier = Modifier.clickable { selectedCategory = cat }
                                ) {
                                    Text(
                                        text = cat,
                                        fontSize = 12.sp,
                                        fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Medium,
                                        color = if (isSelected) BrandBlue else textMutedColor,
                                        modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp)
                                    )
                                }
                            }
                        }

                        // Floating Price asset selector quick chip
                        Surface(
                            shape = RoundedCornerShape(12.dp),
                            color = cardColor,
                            border = BorderStroke(1.dp, borderColor),
                            modifier = Modifier.clickable {
                                // Cycle floating price asset through pinned or defaults
                                val currentList = if (uiState.watchlist.isNotEmpty()) uiState.watchlist.toList() else listOf("BTC", "ETH", "SOL")
                                val currentIndex = currentList.indexOf(uiState.floatingPriceAsset)
                                val nextIndex = (currentIndex + 1) % currentList.size
                                viewModel.setFloatingPriceAsset(currentList[nextIndex])
                            }
                        ) {
                            Row(
                                modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Box(
                                    modifier = Modifier
                                        .size(7.dp)
                                        .clip(CircleShape)
                                        .background(SemanticPositive)
                                )
                                Spacer(modifier = Modifier.width(5.dp))
                                Text(
                                    text = "Widget: ${uiState.floatingPriceAsset}",
                                    fontSize = 11.sp,
                                    fontWeight = FontWeight.SemiBold,
                                    color = BrandGold
                                )
                            }
                        }
                    }
                }

                // Table Header
                item {
                    Surface(
                        shape = RoundedCornerShape(8.dp),
                        color = cardColor,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(horizontal = 14.dp, vertical = 8.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text("Asset / Pair", fontSize = 11.sp, color = textMutedColor, modifier = Modifier.weight(1.3f))
                            Text("Live Price", fontSize = 11.sp, color = textMutedColor, modifier = Modifier.weight(1.1f))
                            Text("24H Change", fontSize = 11.sp, color = textMutedColor, modifier = Modifier.weight(1f))
                            Text("Pin / Float", fontSize = 11.sp, color = textMutedColor, modifier = Modifier.weight(0.9f))
                        }
                    }
                }

                // Empty State
                if (pinnedMarkets.isEmpty()) {
                    item {
                        Surface(
                            shape = RoundedCornerShape(16.dp),
                            color = cardColor,
                            border = BorderStroke(1.dp, borderColor),
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Column(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(32.dp),
                                horizontalAlignment = Alignment.CenterHorizontally,
                                verticalArrangement = Arrangement.Center
                            ) {
                                Icon(
                                    imageVector = Icons.Default.StarOutline,
                                    contentDescription = null,
                                    tint = BrandGold.copy(alpha = 0.6f),
                                    modifier = Modifier.size(48.dp)
                                )
                                Spacer(modifier = Modifier.height(12.dp))
                                Text(
                                    text = "No pinned assets in this list",
                                    fontSize = 15.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = textColor
                                )
                                Spacer(modifier = Modifier.height(6.dp))
                                Text(
                                    text = "Star any crypto asset from the exchange feed or search to monitor it live and track its floating price.",
                                    fontSize = 12.sp,
                                    color = textMutedColor,
                                    lineHeight = 16.sp,
                                    modifier = Modifier.padding(horizontal = 16.dp)
                                )
                                Spacer(modifier = Modifier.height(18.dp))
                                Button(
                                    onClick = {
                                        viewModel.selectTab(MainTab.MARKETS)
                                        viewModel.navigateTo(ScreenRoute.MAIN)
                                    },
                                    colors = ButtonDefaults.buttonColors(containerColor = BrandBlue),
                                    shape = RoundedCornerShape(10.dp)
                                ) {
                                    Icon(Icons.Default.Storefront, contentDescription = null, modifier = Modifier.size(16.dp))
                                    Spacer(modifier = Modifier.width(6.dp))
                                    Text("Browse Exchange Feed", fontSize = 12.sp, fontWeight = FontWeight.SemiBold)
                                }
                            }
                        }
                    }
                } else {
                    // Pinned Market Rows
                    items(pinnedMarkets, key = { it.symbol }) { market ->
                        val isPositive = market.change24h >= 0
                        val badgeColor = if (isPositive) SemanticPositive else SemanticNegative
                        val isFloatingSelected = uiState.floatingPriceAsset == market.asset

                        Surface(
                            shape = RoundedCornerShape(12.dp),
                            color = cardColor,
                            border = BorderStroke(
                                1.dp,
                                if (isFloatingSelected) BrandGold.copy(alpha = 0.6f) else borderColor
                            ),
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
                                .testTag("watchlist_item_${market.asset}")
                        ) {
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(horizontal = 14.dp, vertical = 12.dp),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                // Asset Icon & Name
                                Row(
                                    modifier = Modifier.weight(1.3f),
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Box(
                                        modifier = Modifier
                                            .size(32.dp)
                                            .clip(CircleShape)
                                            .background(if (market.asset == "BTC") BrandGold.copy(alpha = 0.15f) else BrandBlueLight),
                                        contentAlignment = Alignment.Center
                                    ) {
                                        Text(
                                            text = market.asset.take(1),
                                            fontSize = 13.sp,
                                            fontWeight = FontWeight.Bold,
                                            color = if (market.asset == "BTC") BrandGold else BrandBlue
                                        )
                                    }
                                    Spacer(modifier = Modifier.width(8.dp))
                                    Column {
                                        Text(
                                            text = market.asset,
                                            fontSize = 13.sp,
                                            fontWeight = FontWeight.Bold,
                                            color = textColor,
                                            maxLines = 1,
                                            overflow = TextOverflow.Ellipsis
                                        )
                                        Text(
                                            text = market.pair,
                                            fontSize = 10.sp,
                                            color = textMutedColor
                                        )
                                    }
                                }

                                // Live Price
                                Column(modifier = Modifier.weight(1.1f)) {
                                    Text(
                                        text = "$${"%,.2f".format(market.price)}",
                                        fontSize = 13.sp,
                                        fontWeight = FontWeight.Bold,
                                        color = textColor
                                    )
                                    Text(
                                        text = "Vol: $${market.volume24h}",
                                        fontSize = 9.sp,
                                        color = textMutedColor
                                    )
                                }

                                // 24H Change Badge
                                Box(modifier = Modifier.weight(1f)) {
                                    Surface(
                                        shape = RoundedCornerShape(6.dp),
                                        color = badgeColor
                                    ) {
                                        Text(
                                            text = "${if (isPositive) "+" else ""}${"%.2f".format(market.change24h)}%",
                                            fontSize = 11.sp,
                                            fontWeight = FontWeight.Bold,
                                            color = Color.White,
                                            modifier = Modifier.padding(horizontal = 7.dp, vertical = 3.dp)
                                        )
                                    }
                                }

                                // Actions: Star Toggle (Remove) + Float Pin
                                Row(
                                    modifier = Modifier.weight(0.9f),
                                    horizontalArrangement = Arrangement.End,
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    // Set as Floating Icon target
                                    IconButton(
                                        onClick = { viewModel.setFloatingPriceAsset(market.asset) },
                                        modifier = Modifier
                                            .size(28.dp)
                                            .testTag("set_floating_btn_${market.asset}")
                                    ) {
                                        Icon(
                                            imageVector = if (isFloatingSelected) Icons.Default.PushPin else Icons.Default.OutlinedFlag,
                                            contentDescription = "Set Floating Asset",
                                            tint = if (isFloatingSelected) BrandGold else textMutedColor.copy(alpha = 0.5f),
                                            modifier = Modifier.size(16.dp)
                                        )
                                    }

                                    // Remove from Watchlist (Unstar)
                                    IconButton(
                                        onClick = { viewModel.toggleWatchlist(market.asset) },
                                        modifier = Modifier
                                            .size(28.dp)
                                            .testTag("unstar_btn_${market.asset}")
                                    ) {
                                        Icon(
                                            imageVector = Icons.Default.Star,
                                            contentDescription = "Remove from Watchlist",
                                            tint = BrandGold,
                                            modifier = Modifier.size(16.dp)
                                        )
                                    }
                                }
                            }
                        }
                    }
                }

                // Quick Portfolio Threshold Summary Card
                item {
                    Spacer(modifier = Modifier.height(8.dp))
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
                                    Icon(
                                        imageVector = Icons.Default.NotificationsActive,
                                        contentDescription = null,
                                        tint = BrandBlue,
                                        modifier = Modifier.size(16.dp)
                                    )
                                    Spacer(modifier = Modifier.width(6.dp))
                                    Text(
                                        text = "Target Price Alert Thresholds",
                                        fontSize = 12.sp,
                                        fontWeight = FontWeight.Bold,
                                        color = textColor
                                    )
                                }
                                TextButton(
                                    onClick = { viewModel.navigateTo(ScreenRoute.PRICE_THRESHOLDS) },
                                    contentPadding = PaddingValues(0.dp)
                                ) {
                                    Text("Manage", fontSize = 11.sp, color = BrandBlue, fontWeight = FontWeight.Bold)
                                }
                            }

                            HorizontalDivider(color = borderColor, modifier = Modifier.padding(vertical = 8.dp))

                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween
                            ) {
                                Column {
                                    Text("Active Watchlist Items", fontSize = 10.sp, color = textMutedColor)
                                    Text("${uiState.watchlist.size} assets", fontSize = 13.sp, fontWeight = FontWeight.Bold, color = textColor)
                                }
                                Column(horizontalAlignment = Alignment.End) {
                                    Text("Current Floating Asset", fontSize = 10.sp, color = textMutedColor)
                                    Text("${uiState.floatingPriceAsset} / USDT", fontSize = 13.sp, fontWeight = FontWeight.Bold, color = BrandGold)
                                }
                            }
                        }
                    }
                }
            }

            // Draggable Floating Icon of Specific Asset Price
            AnimatedVisibility(
                visible = uiState.isFloatingPriceVisible,
                enter = fadeIn() + scaleIn(),
                exit = fadeOut() + scaleOut(),
                modifier = Modifier
                    .align(Alignment.BottomEnd)
                    .offset { IntOffset(offsetX.roundToInt(), offsetY.roundToInt()) }
                    .padding(end = 20.dp, bottom = 80.dp)
            ) {
                Surface(
                    shape = RoundedCornerShape(20.dp),
                    color = Color(0xFF1E2430),
                    border = BorderStroke(1.5.dp, BrandGold),
                    shadowElevation = 8.dp,
                    modifier = Modifier
                        .shadow(12.dp, shape = RoundedCornerShape(20.dp), spotColor = BrandGold)
                        .pointerInput(Unit) {
                            detectDragGestures { change, dragAmount ->
                                change.consume()
                                offsetX += dragAmount.x
                                offsetY += dragAmount.y
                            }
                        }
                        .clickable {
                            val asset = try {
                                AssetSymbol.valueOf(floatingSymbol)
                            } catch (e: Exception) {
                                AssetSymbol.BTC
                            }
                            viewModel.selectAsset(asset)
                            viewModel.setAssetDetailTab(AssetDetailTab.SPOT)
                            viewModel.navigateTo(ScreenRoute.ASSET_DETAIL)
                        }
                        .testTag("floating_price_icon_widget")
                ) {
                    Row(
                        modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        // Asset Initial Avatar
                        Box(
                            modifier = Modifier
                                .size(28.dp)
                                .clip(CircleShape)
                                .background(Brush.linearGradient(listOf(BrandGold, Color(0xFFFFA500)))),
                            contentAlignment = Alignment.Center
                        ) {
                            Text(
                                text = floatingSymbol.take(1),
                                fontSize = 13.sp,
                                fontWeight = FontWeight.ExtraBold,
                                color = BackgroundDark
                            )
                        }

                        Spacer(modifier = Modifier.width(8.dp))

                        // Asset Symbol and Real-Time Price
                        Column {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Text(
                                    text = floatingSymbol,
                                    fontSize = 12.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = Color.White
                                )
                                Spacer(modifier = Modifier.width(4.dp))
                                Box(
                                    modifier = Modifier
                                        .size(6.dp)
                                        .clip(CircleShape)
                                        .background(SemanticPositive)
                                )
                            }
                            Text(
                                text = "$${"%,.2f".format(floatingPrice)}",
                                fontSize = 12.sp,
                                fontWeight = FontWeight.Bold,
                                color = if (isFloatingPos) SemanticPositive else SemanticNegative
                            )
                        }

                        Spacer(modifier = Modifier.width(8.dp))

                        // Minimize / dismiss button
                        IconButton(
                            onClick = { viewModel.toggleFloatingPriceVisible() },
                            modifier = Modifier.size(20.dp)
                        ) {
                            Icon(
                                imageVector = Icons.Default.Close,
                                contentDescription = "Close floating widget",
                                tint = TextMuted,
                                modifier = Modifier.size(14.dp)
                            )
                        }
                    }
                }
            }
        }
    }
}
