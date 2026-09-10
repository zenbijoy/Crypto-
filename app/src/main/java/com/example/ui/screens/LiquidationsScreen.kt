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
import androidx.compose.ui.graphics.PathEffect
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.ui.theme.*
import com.example.ui.viewmodel.CryptoScopeViewModel
import com.example.ui.viewmodel.ScreenRoute

enum class LiquidationViewMode {
    MAP,
    HEATMAP
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun LiquidationsScreen(viewModel: CryptoScopeViewModel) {
    val uiState by viewModel.uiState.collectAsState()
    val isDark = uiState.isDarkTheme
    val bgColor = if (isDark) DarkBackground else LightBackground
    val cardColor = if (isDark) DarkSurface else LightSurface
    val borderColor = if (isDark) DarkBorder else LightBorder
    val textColor = if (isDark) DarkTextPrimary else LightTextPrimary
    val textMutedColor = if (isDark) DarkTextMuted else LightTextMuted

    var viewMode by remember { mutableStateOf(LiquidationViewMode.MAP) }
    var selectedSymbol by remember { mutableStateOf("Binance/BTCUSDT") }
    var selectedTimeframe by remember { mutableStateOf("1d") }
    var selectedPalette by remember { mutableStateOf("Viridis") }
    var liquidityThreshold by remember { mutableStateOf(1.0f) }

    val overview by viewModel.repository.marketOverview.collectAsState()
    val radarAlerts by viewModel.repository.contractRadarAlerts.collectAsState()
    val livePrices by viewModel.repository.livePrices.collectAsState()

    val btcPrice = livePrices["BTC"] ?: livePrices["BTCUSDT"] ?: 68500.0
    val longLiqFormatted = overview?.liquidations24h?.longLiquidationsFormatted ?: "$120.59M"
    val shortLiqFormatted = overview?.liquidations24h?.shortLiquidationsFormatted ?: "$71.53M"
    val radarCount = radarAlerts.size.takeIf { it > 0 } ?: 6

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text(
                            text = if (viewMode == LiquidationViewMode.MAP) "Liquidation Map" else "Liquidation Heatmap",
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
                    IconButton(onClick = { viewModel.navigateTo(ScreenRoute.SYSTEM_HEALTH) }) {
                        Icon(Icons.Default.Refresh, contentDescription = "Refresh", tint = textColor)
                    }
                    IconButton(onClick = { /* Share */ }) {
                        Icon(Icons.Default.Share, contentDescription = "Share", tint = textColor)
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
                .padding(16.dp)
                .testTag("liquidations_screen"),
            verticalArrangement = Arrangement.spacedBy(14.dp)
        ) {
            // Mode Toggle & Filter Bar
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Map vs Heatmap Toggle
                Surface(
                    shape = RoundedCornerShape(10.dp),
                    color = if (isDark) DarkSurfaceRaised else LightSurfaceRaised
                ) {
                    Row(modifier = Modifier.padding(3.dp)) {
                        listOf(
                            Pair(LiquidationViewMode.MAP, "Map"),
                            Pair(LiquidationViewMode.HEATMAP, "Heatmap")
                        ).forEach { (mode, label) ->
                            val isSelected = viewMode == mode
                            Surface(
                                shape = RoundedCornerShape(8.dp),
                                color = if (isSelected) cardColor else Color.Transparent,
                                modifier = Modifier.clickable { viewMode = mode }
                            ) {
                                Text(
                                    text = label,
                                    fontSize = 12.sp,
                                    fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Normal,
                                    color = if (isSelected) BrandBlue else textMutedColor,
                                    modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp)
                                )
                            }
                        }
                    }
                }

                // AI Analysis Pill Button
                Surface(
                    shape = RoundedCornerShape(16.dp),
                    color = BrandPurpleAI.copy(alpha = 0.15f),
                    border = BorderStroke(1.dp, BrandPurpleAI.copy(alpha = 0.4f)),
                    modifier = Modifier.clickable {
                        viewModel.selectTab(com.example.ui.viewmodel.MainTab.ORDER_FLOW)
                        viewModel.navigateTo(ScreenRoute.MAIN)
                    }
                ) {
                    Row(
                        modifier = Modifier.padding(horizontal = 10.dp, vertical = 5.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            imageVector = Icons.Default.AutoAwesome,
                            contentDescription = null,
                            tint = BrandPurpleAI,
                            modifier = Modifier.size(14.dp)
                        )
                        Spacer(modifier = Modifier.width(4.dp))
                        Text(
                            text = "AI Analysis",
                            fontSize = 11.sp,
                            fontWeight = FontWeight.Bold,
                            color = BrandPurpleAI
                        )
                    }
                }
            }

            // Toolbar Selectors (Symbol, Timeframe, Radar)
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    // Symbol Pill
                    Surface(
                        shape = RoundedCornerShape(8.dp),
                        color = cardColor,
                        border = BorderStroke(1.dp, borderColor)
                    ) {
                        Row(
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(selectedSymbol, fontSize = 11.sp, fontWeight = FontWeight.Bold, color = textColor)
                            Icon(Icons.Default.ArrowDropDown, contentDescription = null, modifier = Modifier.size(16.dp), tint = textMutedColor)
                        }
                    }

                    // Timeframe Selector
                    Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                        listOf("12h", "1d", "3d", "7d").forEach { tf ->
                            val isSel = selectedTimeframe == tf
                            Surface(
                                shape = RoundedCornerShape(6.dp),
                                color = if (isSel) BrandBlue else (if (isDark) DarkSurfaceRaised else LightSurfaceRaised),
                                modifier = Modifier.clickable { selectedTimeframe = tf }
                            ) {
                                Text(
                                    text = tf,
                                    fontSize = 11.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = if (isSel) Color.White else textMutedColor,
                                    modifier = Modifier.padding(horizontal = 7.dp, vertical = 4.dp)
                                )
                            }
                        }
                    }
                }

                // Radar Alert Badge
                Surface(
                    shape = RoundedCornerShape(12.dp),
                    color = SemanticNegative.copy(alpha = 0.12f)
                ) {
                    Row(
                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Box(modifier = Modifier.size(6.dp).clip(CircleShape).background(SemanticNegative))
                        Spacer(modifier = Modifier.width(4.dp))
                        Text("Radar: $radarCount Liqs", fontSize = 10.sp, fontWeight = FontWeight.Bold, color = SemanticNegative)
                    }
                }
            }

            // Overview Summary Metrics Card
            Surface(
                shape = RoundedCornerShape(16.dp),
                color = cardColor,
                border = BorderStroke(1.dp, borderColor),
                modifier = Modifier.fillMaxWidth()
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(14.dp),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Column {
                        Text("Total Long Liquidation", fontSize = 11.sp, color = textMutedColor)
                        Spacer(modifier = Modifier.height(2.dp))
                        Text(longLiqFormatted, fontSize = 17.sp, fontWeight = FontWeight.Bold, color = SemanticNegative)
                        Text("Below $${String.format(java.util.Locale.US, "%,.0f", btcPrice * 0.98)}", fontSize = 10.sp, color = textMutedColor)
                    }
                    Box(modifier = Modifier.width(1.dp).height(44.dp).background(borderColor))
                    Column(horizontalAlignment = Alignment.End) {
                        Text("Total Short Liquidation", fontSize = 11.sp, color = textMutedColor)
                        Spacer(modifier = Modifier.height(2.dp))
                        Text(shortLiqFormatted, fontSize = 17.sp, fontWeight = FontWeight.Bold, color = SemanticPositive)
                        Text("Above $${String.format(java.util.Locale.US, "%,.0f", btcPrice * 1.02)}", fontSize = 10.sp, color = textMutedColor)
                    }
                }
            }

            if (viewMode == LiquidationViewMode.MAP) {
                // Mode 1: Liquidation Distribution Map
                Surface(
                    shape = RoundedCornerShape(16.dp),
                    color = cardColor,
                    border = BorderStroke(1.dp, borderColor),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        // Multi-exchange Legend
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text("Liquidation Leverage Clusters", fontSize = 13.sp, fontWeight = FontWeight.Bold, color = textColor)
                            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                                Row(verticalAlignment = Alignment.CenterVertically) {
                                    Box(modifier = Modifier.size(8.dp).background(BrandBlue, CircleShape))
                                    Spacer(modifier = Modifier.width(3.dp))
                                    Text("Binance", fontSize = 10.sp, color = textMutedColor)
                                }
                                Row(verticalAlignment = Alignment.CenterVertically) {
                                    Box(modifier = Modifier.size(8.dp).background(BybitPurple, CircleShape))
                                    Spacer(modifier = Modifier.width(3.dp))
                                    Text("Bybit", fontSize = 10.sp, color = textMutedColor)
                                }
                                Row(verticalAlignment = Alignment.CenterVertically) {
                                    Box(modifier = Modifier.size(8.dp).background(OkxOrange, CircleShape))
                                    Spacer(modifier = Modifier.width(3.dp))
                                    Text("OKX", fontSize = 10.sp, color = textMutedColor)
                                }
                            }
                        }

                        Spacer(modifier = Modifier.height(14.dp))

                        // Liquidation Map Canvas (Cumulative curves & volume clusters)
                        Canvas(
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(220.dp)
                        ) {
                            val w = size.width
                            val h = size.height
                            val midX = w * 0.45f

                            // Grid lines
                            for (i in 1..4) {
                                val y = h * (i / 5f)
                                drawLine(
                                    color = if (isDark) DarkBorder else LightBorder,
                                    start = Offset(0f, y),
                                    end = Offset(w, y),
                                    strokeWidth = 1f
                                )
                            }

                            // Long Liquidation Bars (Left / Red side)
                            val longBars = listOf(
                                Pair(0.1f, 0.4f),
                                Pair(0.18f, 0.7f),
                                Pair(0.25f, 0.95f),
                                Pair(0.32f, 0.6f),
                                Pair(0.38f, 0.3f)
                            )
                            longBars.forEach { (xPosRatio, heightRatio) ->
                                val barX = w * xPosRatio
                                val barH = h * 0.6f * heightRatio
                                drawRect(
                                    color = SemanticNegative.copy(alpha = 0.85f),
                                    topLeft = Offset(barX - 8f, h - barH),
                                    size = Size(16f, barH)
                                )
                            }

                            // Short Liquidation Bars (Right / Green side)
                            val shortBars = listOf(
                                Pair(0.55f, 0.35f),
                                Pair(0.62f, 0.55f),
                                Pair(0.70f, 0.85f),
                                Pair(0.78f, 0.65f),
                                Pair(0.88f, 0.45f)
                            )
                            shortBars.forEach { (xPosRatio, heightRatio) ->
                                val barX = w * xPosRatio
                                val barH = h * 0.6f * heightRatio
                                drawRect(
                                    color = SemanticPositive.copy(alpha = 0.85f),
                                    topLeft = Offset(barX - 8f, h - barH),
                                    size = Size(16f, barH)
                                )
                            }

                            // Long Cumulative Curve (Red)
                            val longCurve = Path().apply {
                                moveTo(0f, h * 0.95f)
                                lineTo(w * 0.15f, h * 0.8f)
                                lineTo(w * 0.28f, h * 0.35f)
                                lineTo(midX, h * 0.15f)
                            }
                            drawPath(
                                path = longCurve,
                                color = SemanticNegative,
                                style = Stroke(width = 2.5.dp.toPx(), cap = StrokeCap.Round)
                            )

                            // Short Cumulative Curve (Green)
                            val shortCurve = Path().apply {
                                moveTo(midX, h * 0.95f)
                                lineTo(w * 0.65f, h * 0.65f)
                                lineTo(w * 0.82f, h * 0.3f)
                                lineTo(w, h * 0.15f)
                            }
                            drawPath(
                                path = shortCurve,
                                color = SemanticPositive,
                                style = Stroke(width = 2.5.dp.toPx(), cap = StrokeCap.Round)
                            )

                            // Current Price Vertical Pointer Line
                            drawLine(
                                color = Color(0xFFFF4D4F),
                                start = Offset(midX, 0f),
                                end = Offset(midX, h),
                                strokeWidth = 2.dp.toPx(),
                                pathEffect = PathEffect.dashPathEffect(floatArrayOf(10f, 10f), 0f)
                            )
                        }

                        // Current Price Marker Tag
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.Center
                        ) {
                            Surface(
                                shape = RoundedCornerShape(4.dp),
                                color = Color(0xFFFF4D4F)
                            ) {
                                Text(
                                    text = "Current Price: $77,180",
                                    fontSize = 11.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = Color.White,
                                    modifier = Modifier.padding(horizontal = 8.dp, vertical = 2.dp)
                                )
                            }
                        }

                        Spacer(modifier = Modifier.height(10.dp))

                        // Price axis labels
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            listOf("75,386", "76,462", "77,538", "78,614", "79,690", "80,766").forEach { p ->
                                Text(p, fontSize = 9.sp, color = textMutedColor)
                            }
                        }
                    }
                }
            } else {
                // Mode 2: Liquidation Heatmap
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
                            Text("Heatmap Intensity Matrix", fontSize = 13.sp, fontWeight = FontWeight.Bold, color = textColor)

                            // Palette Selector
                            Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                                listOf("Viridis", "Inferno", "Turbo").forEach { p ->
                                    val isP = selectedPalette == p
                                    Surface(
                                        shape = RoundedCornerShape(6.dp),
                                        color = if (isP) BrandBlue else (if (isDark) DarkSurfaceRaised else LightSurfaceRaised),
                                        modifier = Modifier.clickable { selectedPalette = p }
                                    ) {
                                        Text(
                                            text = p,
                                            fontSize = 10.sp,
                                            fontWeight = FontWeight.Bold,
                                            color = if (isP) Color.White else textMutedColor,
                                            modifier = Modifier.padding(horizontal = 6.dp, vertical = 3.dp)
                                        )
                                    }
                                }
                            }
                        }

                        Spacer(modifier = Modifier.height(10.dp))

                        // Liquidity threshold slider
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text("Threshold: ${"%.2f".format(liquidityThreshold)}x", fontSize = 11.sp, color = textMutedColor)
                            Slider(
                                value = liquidityThreshold,
                                onValueChange = { liquidityThreshold = it },
                                valueRange = 0.5f..5.0f,
                                modifier = Modifier.weight(1f).padding(horizontal = 8.dp),
                                colors = SliderDefaults.colors(
                                    thumbColor = BrandBlue,
                                    activeTrackColor = BrandBlue
                                )
                            )
                        }

                        // Heatmap Canvas
                        Canvas(
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(220.dp)
                        ) {
                            val w = size.width
                            val h = size.height

                            // Draw gradient heatmap background blocks
                            val rows = 12
                            val cols = 20
                            val cellW = w / cols
                            val cellH = h / rows

                            for (r in 0 until rows) {
                                for (c in 0 until cols) {
                                    val distFromPrice = kotlin.math.abs(r - 6)
                                    val intensity = (1f - distFromPrice / 6f) * (0.3f + 0.7f * ((c * 7 + r * 13) % 10) / 10f)

                                    val cellColor = when (selectedPalette) {
                                        "Inferno" -> Color(
                                            red = (0.2f + intensity * 0.8f).coerceIn(0f, 1f),
                                            green = (intensity * 0.6f).coerceIn(0f, 1f),
                                            blue = (0.1f + intensity * 0.3f).coerceIn(0f, 1f)
                                        )
                                        "Turbo" -> Color(
                                            red = (intensity * 0.9f).coerceIn(0f, 1f),
                                            green = (0.3f + intensity * 0.7f).coerceIn(0f, 1f),
                                            blue = (1f - intensity * 0.8f).coerceIn(0f, 1f)
                                        )
                                        else -> Color( // Viridis
                                            red = (0.2f + intensity * 0.6f).coerceIn(0f, 1f),
                                            green = (0.1f + intensity * 0.8f).coerceIn(0f, 1f),
                                            blue = (0.4f + (1f - intensity) * 0.5f).coerceIn(0f, 1f)
                                        )
                                    }

                                    drawRect(
                                        color = cellColor.copy(alpha = 0.75f),
                                        topLeft = Offset(c * cellW, r * cellH),
                                        size = Size(cellW - 1f, cellH - 1f)
                                    )
                                }
                            }

                            // Overlaid price candlestick path
                            val priceLine = Path().apply {
                                moveTo(0f, h * 0.65f)
                                lineTo(w * 0.2f, h * 0.55f)
                                lineTo(w * 0.4f, h * 0.7f)
                                lineTo(w * 0.6f, h * 0.45f)
                                lineTo(w * 0.8f, h * 0.35f)
                                lineTo(w, h * 0.48f)
                            }
                            drawPath(
                                path = priceLine,
                                color = Color.White,
                                style = Stroke(width = 2.dp.toPx())
                            )
                        }

                        Spacer(modifier = Modifier.height(8.dp))
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Text("Low Leverage (10x-25x)", fontSize = 10.sp, color = textMutedColor)
                            Text("High Leverage (50x-100x)", fontSize = 10.sp, color = SemanticNegative)
                        }
                    }
                }
            }
        }
    }
}
