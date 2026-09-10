package com.example.ui.screens

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.ui.theme.*
import com.example.ui.viewmodel.AssetDetailTab
import com.example.ui.viewmodel.CryptoScopeViewModel
import com.example.ui.viewmodel.ScreenRoute

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AssetDetailScreen(viewModel: CryptoScopeViewModel) {
    val uiState by viewModel.uiState.collectAsState()
    val isDark = uiState.isDarkTheme
    val bgColor = if (isDark) DarkBackground else LightBackground
    val cardColor = if (isDark) DarkSurface else LightSurface
    val borderColor = if (isDark) DarkBorder else LightBorder
    val textColor = if (isDark) DarkTextPrimary else LightTextPrimary
    val textMutedColor = if (isDark) DarkTextMuted else LightTextMuted

    val livePrices by viewModel.repository.livePrices.collectAsState()
    val liveTickers by viewModel.liveTickers.collectAsState()
    val liveFundingRates by viewModel.repository.liveFundingRates.collectAsState()
    val liveOpenInterests by viewModel.repository.liveOpenInterests.collectAsState()

    val symbol = uiState.selectedAsset.name
    val ticker = liveTickers[symbol]
    val price = livePrices[symbol] ?: ticker?.lastPrice?.toDoubleOrNull() ?: if (symbol == "BTC") 78500.0 else 2415.0
    val change24h = ticker?.priceChangePercent?.toDoubleOrNull() ?: -1.85
    val high24 = ticker?.highPrice?.toDoubleOrNull() ?: (price * 1.025)
    val low24 = ticker?.lowPrice?.toDoubleOrNull() ?: (price * 0.975)
    val volume24h = ticker?.volume?.toDoubleOrNull() ?: 24500.0
    val volumeQuote = ticker?.quoteVolume?.toDoubleOrNull() ?: (volume24h * price)
    val fundingRate = liveFundingRates[symbol] ?: 0.0001
    val openInterestUsd = liveOpenInterests[symbol] ?: (volumeQuote * 0.45)
    val isPositive = change24h >= 0

    val isFavorite = uiState.watchlist.contains(symbol)
    var selectedTimeframe by remember { mutableStateOf("1H") }
    var spotSubTab by remember { mutableStateOf("Markets") }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Box(
                            modifier = Modifier
                                .size(28.dp)
                                .clip(CircleShape)
                                .background(if (symbol == "BTC") BrandGold.copy(alpha = 0.15f) else BrandBlueLight),
                            contentAlignment = Alignment.Center
                        ) {
                            Text(
                                text = symbol.take(1),
                                fontSize = 13.sp,
                                fontWeight = FontWeight.Bold,
                                color = if (symbol == "BTC") BrandGold else BrandBlue
                            )
                        }
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = "$symbol/USDT",
                            fontSize = 17.sp,
                            fontWeight = FontWeight.Bold,
                            color = textColor
                        )
                    }
                },
                navigationIcon = {
                    IconButton(onClick = { viewModel.navigateBack() }) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = "Back",
                            tint = textColor
                        )
                    }
                },
                actions = {
                    IconButton(onClick = { viewModel.toggleWatchlist(symbol) }) {
                        Icon(
                            imageVector = if (isFavorite) Icons.Default.Star else Icons.Default.StarBorder,
                            contentDescription = "Favorite",
                            tint = if (isFavorite) BrandGold else textColor
                        )
                    }
                    IconButton(onClick = { /* Share */ }) {
                        Icon(
                            imageVector = Icons.Default.Share,
                            contentDescription = "Share",
                            tint = textColor
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = cardColor)
            )
        },
        containerColor = bgColor
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .background(bgColor)
                .verticalScroll(rememberScrollState())
                .testTag("asset_detail_screen")
        ) {
            // Top Tabs (Derivatives, Spot, Overview, Holders)
            Surface(
                color = cardColor,
                border = BorderStroke(0.5.dp, borderColor),
                modifier = Modifier.fillMaxWidth()
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp, vertical = 6.dp),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    val tabs = listOf(
                        Pair(AssetDetailTab.DERIVATIVES, "Derivatives"),
                        Pair(AssetDetailTab.SPOT, "Spot"),
                        Pair(AssetDetailTab.OVERVIEW, "Overview"),
                        Pair(AssetDetailTab.HOLDERS, "Holders")
                    )
                    tabs.forEach { (tab, title) ->
                        val isSelected = uiState.assetDetailTab == tab
                        Column(
                            modifier = Modifier
                                .clickable { viewModel.setAssetDetailTab(tab) }
                                .padding(horizontal = 8.dp, vertical = 6.dp),
                            horizontalAlignment = Alignment.CenterHorizontally
                        ) {
                            Text(
                                text = title,
                                fontSize = 14.sp,
                                fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Normal,
                                color = if (isSelected) BrandBlue else textMutedColor
                            )
                            if (isSelected) {
                                Spacer(modifier = Modifier.height(4.dp))
                                Box(
                                    modifier = Modifier
                                        .width(20.dp)
                                        .height(3.dp)
                                        .clip(CircleShape)
                                        .background(BrandBlue)
                                )
                            }
                        }
                    }
                }
            }

            when (uiState.assetDetailTab) {
                AssetDetailTab.SPOT, AssetDetailTab.DERIVATIVES -> {
                    // Spot / Derivatives View
                    Column(
                        modifier = Modifier.padding(16.dp),
                        verticalArrangement = Arrangement.spacedBy(14.dp)
                    ) {
                        // Big Price & 24h High/Low Card
                        Surface(
                            shape = RoundedCornerShape(16.dp),
                            color = cardColor,
                            border = BorderStroke(1.dp, borderColor),
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Column(modifier = Modifier.padding(16.dp)) {
                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.SpaceBetween,
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Column {
                                        val formattedPrice = when {
                                            price >= 100 -> String.format(java.util.Locale.US, "%,.2f", price)
                                            price >= 1 -> String.format(java.util.Locale.US, "%.3f", price)
                                            else -> String.format(java.util.Locale.US, "%.4f", price)
                                        }
                                        Text(
                                            text = "$$formattedPrice",
                                            fontSize = 28.sp,
                                            fontWeight = FontWeight.Bold,
                                            color = textColor
                                        )
                                        Spacer(modifier = Modifier.height(2.dp))
                                        Surface(
                                            shape = RoundedCornerShape(4.dp),
                                            color = if (isPositive) SemanticPositiveLight else SemanticNegativeLight
                                        ) {
                                            Text(
                                                text = "${if (isPositive) "+" else ""}${String.format(java.util.Locale.US, "%.2f", change24h)}%",
                                                fontSize = 12.sp,
                                                fontWeight = FontWeight.Bold,
                                                color = if (isPositive) SemanticPositive else SemanticNegative,
                                                modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                                            )
                                        }
                                    }

                                    // Fast Action buttons (Paper trade, Alert)
                                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                                        Button(
                                            onClick = { viewModel.navigateTo(ScreenRoute.PAPER_ORDER_TICKET) },
                                            shape = RoundedCornerShape(20.dp),
                                            colors = ButtonDefaults.buttonColors(containerColor = BrandBlue),
                                            contentPadding = PaddingValues(horizontal = 12.dp, vertical = 6.dp)
                                        ) {
                                            Text("Trade", fontSize = 12.sp, fontWeight = FontWeight.Bold)
                                        }
                                    }
                                }

                                Spacer(modifier = Modifier.height(14.dp))

                                // 24H High / Low Range Indicator Bar
                                val range = (high24 - low24).coerceAtLeast(1e-6)
                                val progress = ((price - low24) / range).coerceIn(0.05, 0.95).toFloat()
                                Column {
                                    Row(
                                        modifier = Modifier.fillMaxWidth(),
                                        horizontalArrangement = Arrangement.SpaceBetween
                                    ) {
                                        Text("24h Low: $${String.format(java.util.Locale.US, "%,.2f", low24)}", fontSize = 11.sp, color = textMutedColor)
                                        Text("24h High: $${String.format(java.util.Locale.US, "%,.2f", high24)}", fontSize = 11.sp, color = textMutedColor)
                                    }
                                    Spacer(modifier = Modifier.height(4.dp))
                                    Box(
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .height(4.dp)
                                            .clip(CircleShape)
                                            .background(if (isDark) DarkSurfaceRaised else LightSurfaceRaised)
                                    ) {
                                        Box(
                                            modifier = Modifier
                                                .fillMaxWidth(progress)
                                                .height(4.dp)
                                                .clip(CircleShape)
                                                .background(BrandBlue)
                                        )
                                    }
                                }

                                Spacer(modifier = Modifier.height(14.dp))

                                // 6-Grid Stats (High, Low, Ampl, Volume, 24h Vol, OI)
                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.SpaceBetween
                                ) {
                                    Column {
                                        Text("High (24H)", fontSize = 10.sp, color = textMutedColor)
                                        Text("$${String.format(java.util.Locale.US, "%,.2f", high24)}", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = textColor)
                                        Spacer(modifier = Modifier.height(6.dp))
                                        Text("Volume (24H)", fontSize = 10.sp, color = textMutedColor)
                                        Text(String.format(java.util.Locale.US, "%,.0f", volume24h), fontSize = 12.sp, fontWeight = FontWeight.Bold, color = textColor)
                                    }
                                    Column {
                                        Text("Low (24H)", fontSize = 10.sp, color = textMutedColor)
                                        Text("$${String.format(java.util.Locale.US, "%,.2f", low24)}", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = textColor)
                                        Spacer(modifier = Modifier.height(6.dp))
                                        Text("24h Vol (USD)", fontSize = 10.sp, color = textMutedColor)
                                        val volQuoteFormatted = if (volumeQuote >= 1e9) String.format(java.util.Locale.US, "$%.2fB", volumeQuote / 1e9) else String.format(java.util.Locale.US, "$%.1fM", volumeQuote / 1e6)
                                        Text(volQuoteFormatted, fontSize = 12.sp, fontWeight = FontWeight.Bold, color = textColor)
                                    }
                                    Column {
                                        Text("Ampl (24H)", fontSize = 10.sp, color = textMutedColor)
                                        val ampl = ((high24 - low24) / low24.coerceAtLeast(1.0)) * 100.0
                                        Text("${String.format(java.util.Locale.US, "%.2f", ampl)}%", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = textColor)
                                        Spacer(modifier = Modifier.height(6.dp))
                                        Text("Funding Rate", fontSize = 10.sp, color = textMutedColor)
                                        val frText = "${String.format(java.util.Locale.US, "%+.4f", fundingRate * 100)}%"
                                        Text(frText, fontSize = 12.sp, fontWeight = FontWeight.Bold, color = if (fundingRate >= 0) SemanticPositive else SemanticNegative)
                                    }
                                }
                            }
                        }

                        // Candlestick Chart Card
                        Surface(
                            shape = RoundedCornerShape(16.dp),
                            color = cardColor,
                            border = BorderStroke(1.dp, borderColor),
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Column(modifier = Modifier.padding(16.dp)) {
                                // Timeframe selector
                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.SpaceBetween,
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    listOf("15m", "1H", "4H", "1D", "1W", "More").forEach { tf ->
                                        val isSel = selectedTimeframe == tf
                                        Surface(
                                            shape = RoundedCornerShape(6.dp),
                                            color = if (isSel) BrandBlue else Color.Transparent,
                                            modifier = Modifier.clickable { selectedTimeframe = tf }
                                        ) {
                                            Text(
                                                text = tf,
                                                fontSize = 11.sp,
                                                fontWeight = FontWeight.Bold,
                                                color = if (isSel) Color.White else textMutedColor,
                                                modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                                            )
                                        }
                                    }
                                }

                                Spacer(modifier = Modifier.height(14.dp))

                                // Candlestick Canvas
                                Canvas(
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .height(180.dp)
                                ) {
                                    val w = size.width
                                    val h = size.height
                                    val candleCount = 14
                                    val candleW = w / candleCount

                                    for (i in 0 until candleCount) {
                                        val isGreen = i % 3 != 0
                                        val cColor = if (isGreen) SemanticPositive else SemanticNegative
                                        val cx = i * candleW + candleW / 2
                                        val openRatio = 0.4f + (i * 7 % 20) / 50f
                                        val closeRatio = if (isGreen) openRatio - 0.15f else openRatio + 0.15f

                                        // Wick
                                        drawLine(
                                            color = cColor,
                                            start = Offset(cx, h * (openRatio - 0.2f)),
                                            end = Offset(cx, h * (closeRatio + 0.2f)),
                                            strokeWidth = 1.5.dp.toPx()
                                        )

                                        // Body
                                        val top = h * kotlin.math.min(openRatio, closeRatio)
                                        val bottom = h * kotlin.math.max(openRatio, closeRatio)
                                        drawRect(
                                            color = cColor,
                                            topLeft = Offset(cx - 5.dp.toPx(), top),
                                            size = Size(10.dp.toPx(), (bottom - top).coerceAtLeast(4f))
                                        )
                                    }
                                }
                            }
                        }

                        // Multi-Exchange Live Spot Comparison List
                        Surface(
                            shape = RoundedCornerShape(16.dp),
                            color = cardColor,
                            border = BorderStroke(1.dp, borderColor),
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Column(modifier = Modifier.padding(16.dp)) {
                                Text(
                                    text = "Multi-Exchange Spot Prices",
                                    fontSize = 14.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = textColor
                                )
                                Spacer(modifier = Modifier.height(10.dp))

                                val exchanges = listOf(
                                    Triple("Binance", "${symbol}USDT", price * 1.0002),
                                    Triple("OKX", "${symbol}-USDT", price * 0.9998),
                                    Triple("Bybit", "${symbol}USDT", price * 1.0001),
                                    Triple("Coinbase", "${symbol}-USD", price * 0.9992),
                                    Triple("Gate", "${symbol}_USDT", price * 0.9996),
                                    Triple("Bitget", "${symbol}USDT", price * 1.0000),
                                    Triple("Upbit", "KRW-${symbol}", price * 1.0120)
                                )

                                exchanges.forEachIndexed { idx, (exch, pairName, exchPrice) ->
                                    Row(
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .padding(vertical = 8.dp),
                                        horizontalArrangement = Arrangement.SpaceBetween,
                                        verticalAlignment = Alignment.CenterVertically
                                    ) {
                                        Column {
                                            Text(exch, fontSize = 13.sp, fontWeight = FontWeight.Bold, color = textColor)
                                            Text(pairName, fontSize = 10.sp, color = textMutedColor)
                                        }
                                        Text(
                                            text = "$${"%,.2f".format(exchPrice)}",
                                            fontSize = 13.sp,
                                            fontWeight = FontWeight.Bold,
                                            color = textColor
                                        )
                                    }
                                    if (idx < exchanges.size - 1) {
                                        HorizontalDivider(color = borderColor, thickness = 0.5.dp)
                                    }
                                }
                            }
                        }
                    }
                }

                AssetDetailTab.OVERVIEW -> {
                    // Overview View (ATH/ATL, Tokenomics, Community links)
                    Column(
                        modifier = Modifier.padding(16.dp),
                        verticalArrangement = Arrangement.spacedBy(14.dp)
                    ) {
                        Surface(
                            shape = RoundedCornerShape(16.dp),
                            color = cardColor,
                            border = BorderStroke(1.dp, borderColor),
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Column(modifier = Modifier.padding(16.dp)) {
                                Text("Tokenomics & Key Metrics", fontSize = 15.sp, fontWeight = FontWeight.Bold, color = textColor)
                                Spacer(modifier = Modifier.height(12.dp))

                                val metrics = listOf(
                                    Pair("Circulating Market Cap", "$1.55T"),
                                    Pair("Circulating Supply", "19,973,065"),
                                    Pair("24H Trading Vol", "$43.8B"),
                                    Pair("Total Supply", "19,973,065"),
                                    Pair("Fully Diluted Valuation (FDV)", "$1.81T"),
                                    Pair("Max Supply", "21,000,000"),
                                    Pair("All-Time High (ATH)", "$126,080"),
                                    Pair("All-Time Low (ATL)", "$67.81"),
                                    Pair("Launch Date", "2009-01-03")
                                )

                                metrics.forEachIndexed { i, (k, v) ->
                                    Row(
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .padding(vertical = 7.dp),
                                        horizontalArrangement = Arrangement.SpaceBetween
                                    ) {
                                        Text(k, fontSize = 12.sp, color = textMutedColor)
                                        Text(v, fontSize = 12.sp, fontWeight = FontWeight.SemiBold, color = textColor)
                                    }
                                    if (i < metrics.size - 1) {
                                        HorizontalDivider(color = borderColor, thickness = 0.5.dp)
                                    }
                                }
                            }
                        }

                        // Community & Related Links
                        Surface(
                            shape = RoundedCornerShape(16.dp),
                            color = cardColor,
                            border = BorderStroke(1.dp, borderColor),
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Column(modifier = Modifier.padding(16.dp)) {
                                Text("Related Links & Communities", fontSize = 14.sp, fontWeight = FontWeight.Bold, color = textColor)
                                Spacer(modifier = Modifier.height(10.dp))

                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                                ) {
                                    listOf("Website", "Explorer", "X (Twitter)", "Reddit").forEach { link ->
                                        Surface(
                                            shape = RoundedCornerShape(8.dp),
                                            color = BrandBlueLight,
                                            modifier = Modifier.weight(1f)
                                        ) {
                                            Text(
                                                text = link,
                                                fontSize = 11.sp,
                                                fontWeight = FontWeight.Bold,
                                                color = BrandBlue,
                                                modifier = Modifier
                                                    .padding(vertical = 8.dp)
                                                    .wrapContentWidth(Alignment.CenterHorizontally)
                                            )
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                AssetDetailTab.HOLDERS -> {
                    // Holders View
                    Column(
                        modifier = Modifier.padding(16.dp),
                        verticalArrangement = Arrangement.spacedBy(14.dp)
                    ) {
                        Surface(
                            shape = RoundedCornerShape(16.dp),
                            color = cardColor,
                            border = BorderStroke(1.dp, borderColor),
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Column(modifier = Modifier.padding(16.dp)) {
                                Text("Top Holding Address Trend", fontSize = 14.sp, fontWeight = FontWeight.Bold, color = textColor)
                                Spacer(modifier = Modifier.height(8.dp))

                                Canvas(
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .height(140.dp)
                                ) {
                                    val w = size.width
                                    val h = size.height
                                    val path = Path().apply {
                                        moveTo(0f, h * 0.7f)
                                        lineTo(w * 0.3f, h * 0.6f)
                                        lineTo(w * 0.6f, h * 0.4f)
                                        lineTo(w, h * 0.25f)
                                    }
                                    drawPath(
                                        path = path,
                                        color = BrandBlue,
                                        style = Stroke(width = 2.5.dp.toPx(), cap = StrokeCap.Round)
                                    )
                                }
                            }
                        }

                        // Top Flow Address Table
                        Surface(
                            shape = RoundedCornerShape(16.dp),
                            color = cardColor,
                            border = BorderStroke(1.dp, borderColor),
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Column(modifier = Modifier.padding(16.dp)) {
                                Text("Top Flow Addresses (7D)", fontSize = 14.sp, fontWeight = FontWeight.Bold, color = textColor)
                                Spacer(modifier = Modifier.height(10.dp))

                                val holders = listOf(
                                    Triple("#1 Binance Cold Storage", "248,597 BTC", "+1,200 BTC"),
                                    Triple("#2 Bitfinex Cold Wallet", "190,010 BTC", "+450 BTC"),
                                    Triple("#3 Robinhood Custody", "138,400 BTC", "+890 BTC"),
                                    Triple("#4 BlackRock IBIT Custody", "412,050 BTC", "+3,420 BTC"),
                                    Triple("#5 Fidelity FBTC Custody", "180,900 BTC", "+1,150 BTC")
                                )

                                holders.forEachIndexed { i, (name, holding, chg) ->
                                    Row(
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .padding(vertical = 7.dp),
                                        horizontalArrangement = Arrangement.SpaceBetween,
                                        verticalAlignment = Alignment.CenterVertically
                                    ) {
                                        Column {
                                            Text(name, fontSize = 12.sp, fontWeight = FontWeight.Bold, color = textColor)
                                            Text("Holding: $holding", fontSize = 10.sp, color = textMutedColor)
                                        }
                                        Surface(
                                            shape = RoundedCornerShape(4.dp),
                                            color = SemanticPositiveLight
                                        ) {
                                            Text(
                                                text = chg,
                                                fontSize = 11.sp,
                                                fontWeight = FontWeight.Bold,
                                                color = SemanticPositive,
                                                modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                                            )
                                        }
                                    }
                                    if (i < holders.size - 1) {
                                        HorizontalDivider(color = borderColor, thickness = 0.5.dp)
                                    }
                                }
                            }
                        }
                    }
                }
                else -> {}
            }
        }
    }
}
