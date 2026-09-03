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
import androidx.compose.material.icons.automirrored.filled.KeyboardArrowRight
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.core.model.AssetSymbol
import com.example.ui.theme.*
import com.example.ui.viewmodel.AssetDetailTab
import com.example.ui.viewmodel.CryptoScopeViewModel
import com.example.ui.viewmodel.MainTab
import com.example.ui.viewmodel.ScreenRoute

@Composable
fun HomeScreen(viewModel: CryptoScopeViewModel) {
    val uiState by viewModel.uiState.collectAsState()
    val isDark = uiState.isDarkTheme
    val bgColor = if (isDark) DarkBackground else LightBackground
    val cardColor = if (isDark) DarkSurface else LightSurface
    val borderColor = if (isDark) DarkBorder else LightBorder
    val textColor = if (isDark) DarkTextPrimary else LightTextPrimary
    val textMutedColor = if (isDark) DarkTextMuted else LightTextMuted

    val livePrices by viewModel.repository.livePrices.collectAsState()
    val markets = remember(livePrices) { viewModel.repository.getMarkets() }

    var topHeaderTab by remember { mutableStateOf("Market") }
    var selectedMoverTab by remember { mutableStateOf("OI Chg") }
    var selectedLongShortTf by remember { mutableStateOf("24H") }

    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .background(bgColor)
            .padding(horizontal = 16.dp)
            .testTag("home_screen"),
        contentPadding = PaddingValues(top = 12.dp, bottom = 80.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp)
    ) {
        // Top Header (Market, Ranking, Feature + Search & Notifications)
        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(horizontalArrangement = Arrangement.spacedBy(16.dp)) {
                    listOf("Market", "Ranking", "Feature").forEach { tab ->
                        val selected = topHeaderTab == tab
                        Column(
                            modifier = Modifier.clickable { topHeaderTab = tab },
                            horizontalAlignment = Alignment.CenterHorizontally
                        ) {
                            Text(
                                text = tab,
                                fontSize = 18.sp,
                                fontWeight = if (selected) FontWeight.Bold else FontWeight.Normal,
                                color = if (selected) textColor else textMutedColor
                            )
                            if (selected) {
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

                Row(verticalAlignment = Alignment.CenterVertically) {
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
                    IconButton(
                        onClick = { viewModel.navigateTo(ScreenRoute.NOTIFICATIONS) },
                        modifier = Modifier.size(36.dp)
                    ) {
                        BadgedBox(
                            badge = {
                                Badge(
                                    containerColor = SemanticNegative,
                                    contentColor = Color.White
                                ) {
                                    Text("3", fontSize = 8.sp)
                                }
                            }
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
            }
        }

        // Referral Promo Banner
        item {
            Surface(
                shape = RoundedCornerShape(16.dp),
                color = Color.Transparent,
                modifier = Modifier.fillMaxWidth()
            ) {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .background(
                            brush = Brush.horizontalGradient(
                                colors = listOf(Color(0xFF2F54EB), Color(0xFF597EF7), Color(0xFF85A5FF))
                            ),
                            shape = RoundedCornerShape(16.dp)
                        )
                        .padding(16.dp)
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column(modifier = Modifier.weight(1f)) {
                            Text(
                                text = "CryptoScope Referral Program",
                                fontSize = 15.sp,
                                fontWeight = FontWeight.Bold,
                                color = Color.White
                            )
                            Spacer(modifier = Modifier.height(4.dp))
                            Text(
                                text = "Invite friends, earn points, rebates! Direct USDT Rewards!",
                                fontSize = 11.sp,
                                color = Color.White.copy(alpha = 0.85f)
                            )
                        }
                        Icon(
                            imageVector = Icons.Default.CardGiftcard,
                            contentDescription = null,
                            tint = Color.White,
                            modifier = Modifier.size(36.dp)
                        )
                    }
                }
            }
        }

        // Fear & Greed Quick Pill
        item {
            Surface(
                shape = RoundedCornerShape(20.dp),
                color = SemanticPositiveLight,
                border = BorderStroke(1.dp, SemanticPositive.copy(alpha = 0.3f)),
                modifier = Modifier
                    .fillMaxWidth()
                    .clickable { viewModel.navigateTo(ScreenRoute.FEAR_AND_GREED_DETAIL) }
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 14.dp, vertical = 8.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Box(
                            modifier = Modifier
                                .size(8.dp)
                                .clip(CircleShape)
                                .background(SemanticPositive)
                        )
                        Spacer(modifier = Modifier.width(6.dp))
                        Text(
                            text = "Greed",
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Bold,
                            color = SemanticPositive
                        )
                    }

                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text(
                            text = "Fear and Greed 70",
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Bold,
                            color = SemanticPositive
                        )
                        Spacer(modifier = Modifier.width(4.dp))
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.KeyboardArrowRight,
                            contentDescription = null,
                            tint = SemanticPositive,
                            modifier = Modifier.size(16.dp)
                        )
                    }
                }
            }
        }

        // 4-Metric Overview Grid Card
        item {
            Surface(
                shape = RoundedCornerShape(16.dp),
                color = cardColor,
                border = BorderStroke(1.dp, borderColor),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        // Total Futures OI
                        Column(modifier = Modifier.weight(1f)) {
                            Text("Total Futures OI", fontSize = 11.sp, color = textMutedColor)
                            Spacer(modifier = Modifier.height(2.dp))
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Text("106.9B", fontSize = 16.sp, fontWeight = FontWeight.Bold, color = textColor)
                                Spacer(modifier = Modifier.width(4.dp))
                                Text("▼ 1.05%", fontSize = 10.sp, fontWeight = FontWeight.Bold, color = SemanticNegative)
                            }
                        }

                        // 24H Futures Volume
                        Column(modifier = Modifier.weight(1f)) {
                            Text("24H Futures Volume", fontSize = 11.sp, color = textMutedColor)
                            Spacer(modifier = Modifier.height(2.dp))
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Text("141.3B", fontSize = 16.sp, fontWeight = FontWeight.Bold, color = textColor)
                                Spacer(modifier = Modifier.width(4.dp))
                                Text("▼ 14.53%", fontSize = 10.sp, fontWeight = FontWeight.Bold, color = SemanticNegative)
                            }
                        }
                    }

                    Spacer(modifier = Modifier.height(14.dp))
                    HorizontalDivider(color = borderColor, thickness = 0.5.dp)
                    Spacer(modifier = Modifier.height(14.dp))

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        // Longs Shorts Person Ratio
                        Column(modifier = Modifier.weight(1f)) {
                            Text("Longs Shorts Ratio", fontSize = 11.sp, color = textMutedColor)
                            Spacer(modifier = Modifier.height(2.dp))
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Text("1.23", fontSize = 16.sp, fontWeight = FontWeight.Bold, color = textColor)
                                Spacer(modifier = Modifier.width(4.dp))
                                Text("▲ 20.00%", fontSize = 10.sp, fontWeight = FontWeight.Bold, color = SemanticPositive)
                            }
                        }

                        // Liquidation Data
                        Column(modifier = Modifier.weight(1f)) {
                            Text("Liquidation (24H)", fontSize = 11.sp, color = textMutedColor)
                            Spacer(modifier = Modifier.height(2.dp))
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Text("L $120.5M", fontSize = 11.sp, fontWeight = FontWeight.Bold, color = SemanticNegative)
                                Spacer(modifier = Modifier.width(6.dp))
                                Text("S $71.5M", fontSize = 11.sp, fontWeight = FontWeight.Bold, color = SemanticPositive)
                            }
                        }
                    }
                }
            }
        }

        // Contract Radar Banner
        item {
            Surface(
                shape = RoundedCornerShape(12.dp),
                color = if (isDark) DarkSurfaceRaised else LightSurfaceRaised,
                border = BorderStroke(1.dp, borderColor),
                modifier = Modifier
                    .fillMaxWidth()
                    .clickable { viewModel.navigateTo(ScreenRoute.LIQUIDATION_MAP) }
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 12.dp, vertical = 10.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(
                            imageVector = Icons.Default.Radar,
                            contentDescription = null,
                            tint = SemanticNegative,
                            modifier = Modifier.size(18.dp)
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = "Contract Radar · BTC Liquidation Pool at 77.2K",
                            fontSize = 12.sp,
                            fontWeight = FontWeight.SemiBold,
                            color = textColor
                        )
                    }

                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Surface(
                            shape = RoundedCornerShape(10.dp),
                            color = SemanticNegativeLight
                        ) {
                            Text(
                                text = "82",
                                fontSize = 10.sp,
                                fontWeight = FontWeight.Bold,
                                color = SemanticNegative,
                                modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                            )
                        }
                        Spacer(modifier = Modifier.width(4.dp))
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.KeyboardArrowRight,
                            contentDescription = null,
                            tint = textMutedColor,
                            modifier = Modifier.size(16.dp)
                        )
                    }
                }
            }
        }

        // 8-Grid Feature Shortcuts
        item {
            val features = listOf(
                FeatureItem("AI Analyze", Icons.Default.AutoAwesome, BrandPurpleAI, hasAiBadge = true) {
                    viewModel.selectTab(MainTab.ORDER_FLOW)
                    viewModel.navigateTo(ScreenRoute.MAIN)
                },
                FeatureItem("Fund Flow", Icons.Default.AccountBalance, BrandBlue) {
                    viewModel.navigateTo(ScreenRoute.ETF_FLOW)
                },
                FeatureItem("Aggregated Book", Icons.Default.CandlestickChart, BrandGold) {
                    viewModel.navigateTo(ScreenRoute.AGGREGATED_ORDERBOOK)
                },
                FeatureItem("Visual Screener", Icons.Default.Visibility, BrandPurpleAI) {
                    viewModel.selectTab(MainTab.MARKETS)
                    viewModel.navigateTo(ScreenRoute.MAIN)
                },
                FeatureItem("Liquidation Map", Icons.Default.BarChart, SemanticNegative) {
                    viewModel.navigateTo(ScreenRoute.LIQUIDATION_MAP)
                },
                FeatureItem("ETF Flow", Icons.Default.PieChart, SemanticPositive) {
                    viewModel.navigateTo(ScreenRoute.ETF_FLOW)
                },
                FeatureItem("Funding Heatmap", Icons.Default.GridOn, Color(0xFF13C2C2)) {
                    viewModel.navigateTo(ScreenRoute.FUNDING_HEATMAP)
                },
                FeatureItem("More Hub", Icons.Default.GridView, BrandBlue) {
                    viewModel.selectTab(MainTab.USER_CENTER)
                    viewModel.navigateTo(ScreenRoute.MAIN)
                }
            )

            Surface(
                shape = RoundedCornerShape(16.dp),
                color = cardColor,
                border = BorderStroke(1.dp, borderColor),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(14.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        features.take(4).forEach { feat ->
                            FeatureIconView(feat, textColor, textMutedColor)
                        }
                    }
                    Spacer(modifier = Modifier.height(14.dp))
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        features.drop(4).take(4).forEach { feat ->
                            FeatureIconView(feat, textColor, textMutedColor)
                        }
                    }
                }
            }
        }

        // 3-Card Sentiment & Dominance Row
        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(10.dp)
            ) {
                // Fear & Greed Card
                Surface(
                    shape = RoundedCornerShape(14.dp),
                    color = cardColor,
                    border = BorderStroke(1.dp, borderColor),
                    modifier = Modifier
                        .weight(1f)
                        .clickable { viewModel.navigateTo(ScreenRoute.FEAR_AND_GREED_DETAIL) }
                ) {
                    Column(modifier = Modifier.padding(12.dp)) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text("Fear & Greed", fontSize = 11.sp, fontWeight = FontWeight.Bold, color = textColor)
                            Icon(Icons.AutoMirrored.Filled.KeyboardArrowRight, contentDescription = null, tint = textMutedColor, modifier = Modifier.size(12.dp))
                        }
                        Spacer(modifier = Modifier.height(6.dp))
                        Text("70", fontSize = 20.sp, fontWeight = FontWeight.Bold, color = SemanticPositive)
                        Text("Greed", fontSize = 10.sp, fontWeight = FontWeight.Bold, color = SemanticPositive)
                    }
                }

                // BTC Market Cap Dominance Card
                Surface(
                    shape = RoundedCornerShape(14.dp),
                    color = cardColor,
                    border = BorderStroke(1.dp, borderColor),
                    modifier = Modifier.weight(1f)
                ) {
                    Column(modifier = Modifier.padding(12.dp)) {
                        Text("BTC Dominance", fontSize = 11.sp, fontWeight = FontWeight.Bold, color = textColor)
                        Spacer(modifier = Modifier.height(6.dp))
                        Text("59.73%", fontSize = 20.sp, fontWeight = FontWeight.Bold, color = textColor)
                        Text("▼ 0.02%", fontSize = 10.sp, fontWeight = FontWeight.Bold, color = SemanticNegative)
                    }
                }

                // Altcoin Season Index Card
                Surface(
                    shape = RoundedCornerShape(14.dp),
                    color = cardColor,
                    border = BorderStroke(1.dp, borderColor),
                    modifier = Modifier.weight(1f)
                ) {
                    Column(modifier = Modifier.padding(12.dp)) {
                        Text("Altcoin Season", fontSize = 11.sp, fontWeight = FontWeight.Bold, color = textColor)
                        Spacer(modifier = Modifier.height(6.dp))
                        Text("51 / 100", fontSize = 20.sp, fontWeight = FontWeight.Bold, color = BrandGold)
                        Text("Alt Season", fontSize = 10.sp, fontWeight = FontWeight.Bold, color = BrandGold)
                    }
                }
            }
        }

        // Liquidation Data Dual-Axis Chart Card
        item {
            Surface(
                shape = RoundedCornerShape(16.dp),
                color = cardColor,
                border = BorderStroke(1.dp, borderColor),
                modifier = Modifier
                    .fillMaxWidth()
                    .clickable { viewModel.navigateTo(ScreenRoute.LIQUIDATION_MAP) }
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Text("Liquidation Data", fontSize = 14.sp, fontWeight = FontWeight.Bold, color = textColor)
                                Spacer(modifier = Modifier.width(4.dp))
                                Icon(Icons.AutoMirrored.Filled.KeyboardArrowRight, contentDescription = null, tint = textMutedColor, modifier = Modifier.size(16.dp))
                            }
                            Spacer(modifier = Modifier.height(2.dp))
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Text("$192.12M", fontSize = 18.sp, fontWeight = FontWeight.Bold, color = textColor)
                                Spacer(modifier = Modifier.width(6.dp))
                                Text("▲ 30.84%", fontSize = 11.sp, fontWeight = FontWeight.Bold, color = SemanticPositive)
                            }
                        }

                        // Legend
                        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Box(modifier = Modifier.size(6.dp).background(BrandGold, CircleShape))
                                Spacer(modifier = Modifier.width(3.dp))
                                Text("Price", fontSize = 10.sp, color = textMutedColor)
                            }
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Box(modifier = Modifier.size(6.dp).background(SemanticPositive, CircleShape))
                                Spacer(modifier = Modifier.width(3.dp))
                                Text("Longs", fontSize = 10.sp, color = textMutedColor)
                            }
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Box(modifier = Modifier.size(6.dp).background(SemanticNegative, CircleShape))
                                Spacer(modifier = Modifier.width(3.dp))
                                Text("Shorts", fontSize = 10.sp, color = textMutedColor)
                            }
                        }
                    }

                    Spacer(modifier = Modifier.height(14.dp))

                    // Dual Axis Canvas
                    Canvas(
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(130.dp)
                    ) {
                        val w = size.width
                        val h = size.height
                        val bars = 8
                        val barW = w / (bars * 2)

                        // Grid lines
                        for (i in 1..3) {
                            val y = h * (i / 4f)
                            drawLine(
                                color = if (isDark) DarkBorder else LightBorder,
                                start = Offset(0f, y),
                                end = Offset(w, y),
                                strokeWidth = 1f
                            )
                        }

                        // Long bars (green) & Short bars (red)
                        for (i in 0 until bars) {
                            val bx = i * (barW * 2) + 8.dp.toPx()
                            val longH = h * 0.4f * ((i * 3 % 7 + 2) / 9f)
                            val shortH = h * 0.35f * (((i + 2) * 5 % 6 + 1) / 7f)

                            drawRect(
                                color = SemanticPositive,
                                topLeft = Offset(bx, h - longH),
                                size = Size(barW - 4.dp.toPx(), longH)
                            )

                            drawRect(
                                color = SemanticNegative,
                                topLeft = Offset(bx + barW, h - shortH),
                                size = Size(barW - 4.dp.toPx(), shortH)
                            )
                        }

                        // Overlaid price line (gold)
                        val pricePath = Path().apply {
                            moveTo(0f, h * 0.7f)
                            lineTo(w * 0.25f, h * 0.55f)
                            lineTo(w * 0.5f, h * 0.6f)
                            lineTo(w * 0.75f, h * 0.35f)
                            lineTo(w, h * 0.2f)
                        }
                        drawPath(
                            path = pricePath,
                            color = BrandGold,
                            style = Stroke(width = 2.dp.toPx(), cap = StrokeCap.Round)
                        )
                    }
                }
            }
        }

        // Longs VS Shorts Card
        item {
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
                        Text("Longs VS Shorts", fontSize = 14.sp, fontWeight = FontWeight.Bold, color = textColor)

                        // Timeframe buttons
                        Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                            listOf("5m", "1H", "4H", "24H").forEach { tf ->
                                val isSel = selectedLongShortTf == tf
                                Surface(
                                    shape = RoundedCornerShape(6.dp),
                                    color = if (isSel) BrandBlue else (if (isDark) DarkSurfaceRaised else LightSurfaceRaised),
                                    modifier = Modifier.clickable { selectedLongShortTf = tf }
                                ) {
                                    Text(
                                        text = tf,
                                        fontSize = 10.sp,
                                        fontWeight = FontWeight.Bold,
                                        color = if (isSel) Color.White else textMutedColor,
                                        modifier = Modifier.padding(horizontal = 6.dp, vertical = 3.dp)
                                    )
                                }
                            }
                        }
                    }

                    Spacer(modifier = Modifier.height(10.dp))

                    Text("BTC Taker Buy/Sell Ratio: 0.95", fontSize = 12.sp, color = textMutedColor)

                    Spacer(modifier = Modifier.height(8.dp))

                    // Split progress bar (Green Longs / Red Shorts)
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(18.dp)
                            .clip(RoundedCornerShape(9.dp))
                    ) {
                        Box(
                            modifier = Modifier
                                .weight(0.4867f)
                                .fillMaxHeight()
                                .background(SemanticPositive)
                                .padding(start = 8.dp),
                            contentAlignment = Alignment.CenterStart
                        ) {
                            Text("Longs 48.67%", fontSize = 9.sp, fontWeight = FontWeight.Bold, color = Color.White)
                        }
                        Box(
                            modifier = Modifier
                                .weight(0.5133f)
                                .fillMaxHeight()
                                .background(SemanticNegative)
                                .padding(end = 8.dp),
                            contentAlignment = Alignment.CenterEnd
                        ) {
                            Text("Shorts 51.33%", fontSize = 9.sp, fontWeight = FontWeight.Bold, color = Color.White)
                        }
                    }
                }
            }
        }

        // Market Mover Tabbed List (OI Chg, Funding Rate, Gainers, Losers)
        item {
            Surface(
                shape = RoundedCornerShape(16.dp),
                color = cardColor,
                border = BorderStroke(1.dp, borderColor),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    // Mover Tabs
                    LazyRow(
                        horizontalArrangement = Arrangement.spacedBy(14.dp),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        items(listOf("OI Chg", "Funding Rate", "Gainers", "Losers")) { tab ->
                            val selected = selectedMoverTab == tab
                            Column(
                                modifier = Modifier.clickable { selectedMoverTab = tab },
                                horizontalAlignment = Alignment.CenterHorizontally
                            ) {
                                Text(
                                    text = tab,
                                    fontSize = 13.sp,
                                    fontWeight = if (selected) FontWeight.Bold else FontWeight.Normal,
                                    color = if (selected) BrandBlue else textMutedColor
                                )
                                if (selected) {
                                    Spacer(modifier = Modifier.height(4.dp))
                                    Box(
                                        modifier = Modifier
                                            .width(18.dp)
                                            .height(2.5.dp)
                                            .clip(CircleShape)
                                            .background(BrandBlue)
                                    )
                                }
                            }
                        }
                    }

                    Spacer(modifier = Modifier.height(14.dp))

                    // Column headers
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text("Coin / OI", fontSize = 11.sp, color = textMutedColor)
                        Text("Price", fontSize = 11.sp, color = textMutedColor)
                        Text("24H Chg", fontSize = 11.sp, color = textMutedColor)
                    }

                    Spacer(modifier = Modifier.height(8.dp))

                    // Coin rows
                    markets.take(5).forEachIndexed { idx, market ->
                        val isPos = market.change24h >= 0
                        val badgeCol = if (isPos) SemanticPositive else SemanticNegative

                        Row(
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
                                .padding(vertical = 8.dp),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Box(
                                    modifier = Modifier
                                        .size(28.dp)
                                        .clip(CircleShape)
                                        .background(if (market.asset == "BTC") BrandGold.copy(alpha = 0.15f) else BrandBlueLight),
                                    contentAlignment = Alignment.Center
                                ) {
                                    Text(
                                        text = market.asset.take(1),
                                        fontSize = 12.sp,
                                        fontWeight = FontWeight.Bold,
                                        color = if (market.asset == "BTC") BrandGold else BrandBlue
                                    )
                                }
                                Spacer(modifier = Modifier.width(8.dp))
                                Column {
                                    Text(market.asset, fontSize = 13.sp, fontWeight = FontWeight.Bold, color = textColor)
                                    Text("OI: $${market.volume24h}", fontSize = 10.sp, color = textMutedColor)
                                }
                            }

                            Text("$${"%,.2f".format(market.price)}", fontSize = 13.sp, fontWeight = FontWeight.Bold, color = textColor)

                            Surface(
                                shape = RoundedCornerShape(4.dp),
                                color = badgeCol
                            ) {
                                Text(
                                    text = "${if (isPos) "+" else ""}${"%.2f".format(market.change24h)}%",
                                    fontSize = 11.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = Color.White,
                                    modifier = Modifier.padding(horizontal = 8.dp, vertical = 3.dp)
                                )
                            }
                        }

                        if (idx < 4) {
                            HorizontalDivider(color = borderColor, thickness = 0.5.dp)
                        }
                    }
                }
            }
        }
    }
}

data class FeatureItem(
    val title: String,
    val icon: ImageVector,
    val color: Color,
    val hasAiBadge: Boolean = false,
    val onClick: () -> Unit
)

@Composable
fun FeatureIconView(
    item: FeatureItem,
    textColor: Color,
    textMutedColor: Color
) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        modifier = Modifier
            .width(68.dp)
            .clickable { item.onClick() }
    ) {
        Box(contentAlignment = Alignment.TopEnd) {
            Box(
                modifier = Modifier
                    .size(46.dp)
                    .clip(CircleShape)
                    .background(item.color.copy(alpha = 0.12f)),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = item.icon,
                    contentDescription = item.title,
                    tint = item.color,
                    modifier = Modifier.size(22.dp)
                )
            }

            if (item.hasAiBadge) {
                Surface(
                    shape = RoundedCornerShape(6.dp),
                    color = BrandPurpleAI
                ) {
                    Text(
                        text = "+AI",
                        fontSize = 8.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color.White,
                        modifier = Modifier.padding(horizontal = 3.dp, vertical = 1.dp)
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(6.dp))

        Text(
            text = item.title,
            fontSize = 11.sp,
            fontWeight = FontWeight.Medium,
            color = textColor,
            maxLines = 1
        )
    }
}
