package com.example.ui.screens

import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
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
import androidx.compose.material.icons.filled.Share
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
import com.example.ui.viewmodel.CryptoScopeViewModel
import kotlin.math.cos
import kotlin.math.sin

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun FearAndGreedScreen(viewModel: CryptoScopeViewModel) {
    val uiState by viewModel.uiState.collectAsState()
    val isDark = uiState.isDarkTheme
    val bgColor = if (isDark) DarkBackground else LightBackground
    val cardColor = if (isDark) DarkSurface else LightSurface
    val borderColor = if (isDark) DarkBorder else LightBorder
    val textColor = if (isDark) DarkTextPrimary else LightTextPrimary
    val textMutedColor = if (isDark) DarkTextMuted else LightTextMuted

    var selectedTimeline by remember { mutableStateOf("All") }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Text(
                        text = "Fear and Greed",
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold,
                        color = textColor
                    )
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
                    IconButton(onClick = { /* Share */ }) {
                        Icon(
                            imageVector = Icons.Default.Share,
                            contentDescription = "Share",
                            tint = textColor
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = cardColor
                )
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
                .testTag("fear_and_greed_screen"),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Speedometer Gauge Card
            Surface(
                shape = RoundedCornerShape(16.dp),
                color = cardColor,
                border = BorderStroke(1.dp, borderColor),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(
                    modifier = Modifier.padding(20.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    SpeedometerArcGauge(
                        score = 70,
                        label = "Greed",
                        isDark = isDark
                    )

                    Spacer(modifier = Modifier.height(16.dp))

                    Text(
                        text = "Fear & Greed Index evaluates crypto market sentiment based on volatility, volume, social media, and market momentum.",
                        fontSize = 12.sp,
                        color = textMutedColor,
                        lineHeight = 18.sp
                    )
                }
            }

            // Historical Compare Card
            Surface(
                shape = RoundedCornerShape(16.dp),
                color = cardColor,
                border = BorderStroke(1.dp, borderColor),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(
                        text = "Historical Compare",
                        fontSize = 15.sp,
                        fontWeight = FontWeight.Bold,
                        color = textColor
                    )
                    Spacer(modifier = Modifier.height(14.dp))

                    val historyItems = listOf(
                        Triple("Yesterday", "Greed-61", SemanticPositive),
                        Triple("7 days ago", "Greed-73", SemanticPositive),
                        Triple("30 days ago", "Fear-28", SemanticNegative)
                    )

                    historyItems.forEachIndexed { index, (period, sentiment, color) ->
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(vertical = 8.dp),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(
                                text = period,
                                fontSize = 14.sp,
                                color = textMutedColor
                            )
                            Surface(
                                shape = RoundedCornerShape(6.dp),
                                color = color.copy(alpha = 0.15f)
                            ) {
                                Text(
                                    text = sentiment,
                                    fontSize = 13.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = color,
                                    modifier = Modifier.padding(horizontal = 10.dp, vertical = 4.dp)
                                )
                            }
                        }
                        if (index < historyItems.size - 1) {
                            HorizontalDivider(color = borderColor, thickness = 0.5.dp)
                        }
                    }
                }
            }

            // Year Stats Card
            Surface(
                shape = RoundedCornerShape(16.dp),
                color = cardColor,
                border = BorderStroke(1.dp, borderColor),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(
                        text = "Year Stats",
                        fontSize = 15.sp,
                        fontWeight = FontWeight.Bold,
                        color = textColor
                    )
                    Spacer(modifier = Modifier.height(14.dp))

                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(vertical = 6.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column {
                            Text("Year High", fontSize = 14.sp, fontWeight = FontWeight.SemiBold, color = textColor)
                            Text("2026-08-24", fontSize = 11.sp, color = textMutedColor)
                        }
                        Surface(
                            shape = RoundedCornerShape(6.dp),
                            color = Color(0xFFFF4D4F).copy(alpha = 0.15f)
                        ) {
                            Text(
                                text = "Greed-74",
                                fontSize = 13.sp,
                                fontWeight = FontWeight.Bold,
                                color = Color(0xFFFF4D4F),
                                modifier = Modifier.padding(horizontal = 10.dp, vertical = 4.dp)
                            )
                        }
                    }

                    HorizontalDivider(color = borderColor, thickness = 0.5.dp, modifier = Modifier.padding(vertical = 4.dp))

                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(vertical = 6.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column {
                            Text("Year Low", fontSize = 14.sp, fontWeight = FontWeight.SemiBold, color = textColor)
                            Text("2026-02-07", fontSize = 11.sp, color = textMutedColor)
                        }
                        Surface(
                            shape = RoundedCornerShape(6.dp),
                            color = Color(0xFF13C2C2).copy(alpha = 0.15f)
                        ) {
                            Text(
                                text = "Extreme Fear-5",
                                fontSize = 13.sp,
                                fontWeight = FontWeight.Bold,
                                color = Color(0xFF13C2C2),
                                modifier = Modifier.padding(horizontal = 10.dp, vertical = 4.dp)
                            )
                        }
                    }
                }
            }

            // Fear and Greed vs BTC Price Interactive Chart
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
                        Text(
                            text = "Historical Trend",
                            fontSize = 15.sp,
                            fontWeight = FontWeight.Bold,
                            color = textColor
                        )
                        Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                            listOf("1M", "1Y", "All").forEach { period ->
                                val selected = selectedTimeline == period
                                Surface(
                                    shape = RoundedCornerShape(12.dp),
                                    color = if (selected) BrandBlue else (if (isDark) DarkSurfaceRaised else LightSurfaceRaised),
                                    modifier = Modifier.clickable { selectedTimeline = period }
                                ) {
                                    Text(
                                        text = period,
                                        fontSize = 11.sp,
                                        fontWeight = FontWeight.Bold,
                                        color = if (selected) Color.White else textMutedColor,
                                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 3.dp)
                                    )
                                }
                            }
                        }
                    }

                    Spacer(modifier = Modifier.height(8.dp))

                    // Legend
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Box(modifier = Modifier.size(8.dp).background(SemanticPositive, CircleShape))
                            Spacer(modifier = Modifier.width(4.dp))
                            Text("Fear & Greed", fontSize = 11.sp, color = textMutedColor)
                        }
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Box(modifier = Modifier.size(8.dp).background(BrandGold, CircleShape))
                            Spacer(modifier = Modifier.width(4.dp))
                            Text("BTC Price", fontSize = 11.sp, color = textMutedColor)
                        }
                    }

                    Spacer(modifier = Modifier.height(14.dp))

                    // Canvas chart
                    Canvas(
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(160.dp)
                    ) {
                        val width = size.width
                        val height = size.height

                        // Grid lines
                        for (i in 1..4) {
                            val y = height * (i / 5f)
                            drawLine(
                                color = if (isDark) DarkBorder else LightBorder,
                                start = Offset(0f, y),
                                end = Offset(width, y),
                                strokeWidth = 1f
                            )
                        }

                        // Fear and greed area
                        val sentimentPoints = listOf(
                            Offset(0f, height * 0.7f),
                            Offset(width * 0.2f, height * 0.85f),
                            Offset(width * 0.4f, height * 0.45f),
                            Offset(width * 0.6f, height * 0.6f),
                            Offset(width * 0.8f, height * 0.35f),
                            Offset(width, height * 0.3f)
                        )

                        val sentimentPath = Path().apply {
                            moveTo(0f, height)
                            sentimentPoints.forEach { lineTo(it.x, it.y) }
                            lineTo(width, height)
                            close()
                        }

                        drawPath(
                            path = sentimentPath,
                            color = SemanticPositive.copy(alpha = 0.2f)
                        )

                        // BTC Price line
                        val btcPoints = listOf(
                            Offset(0f, height * 0.8f),
                            Offset(width * 0.2f, height * 0.75f),
                            Offset(width * 0.4f, height * 0.5f),
                            Offset(width * 0.6f, height * 0.4f),
                            Offset(width * 0.8f, height * 0.25f),
                            Offset(width, height * 0.15f)
                        )

                        val btcPath = Path().apply {
                            moveTo(btcPoints.first().x, btcPoints.first().y)
                            for (p in btcPoints) lineTo(p.x, p.y)
                        }

                        drawPath(
                            path = btcPath,
                            color = BrandGold,
                            style = Stroke(width = 2.5.dp.toPx(), cap = StrokeCap.Round)
                        )
                    }

                    Spacer(modifier = Modifier.height(8.dp))
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text("2025-09", fontSize = 10.sp, color = textMutedColor)
                        Text("2026-01", fontSize = 10.sp, color = textMutedColor)
                        Text("2026-05", fontSize = 10.sp, color = textMutedColor)
                        Text("2026-09", fontSize = 10.sp, color = textMutedColor)
                    }
                }
            }
        }
    }
}

@Composable
fun SpeedometerArcGauge(
    score: Int,
    label: String,
    isDark: Boolean,
    modifier: Modifier = Modifier
) {
    val animatedScore by animateFloatAsState(
        targetValue = score.toFloat(),
        animationSpec = tween(1000),
        label = "gauge_needle"
    )

    val textColor = if (isDark) DarkTextPrimary else LightTextPrimary
    val textMutedColor = if (isDark) DarkTextMuted else LightTextMuted

    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        modifier = modifier.fillMaxWidth()
    ) {
        Box(
            contentAlignment = Alignment.BottomCenter,
            modifier = Modifier
                .size(width = 240.dp, height = 135.dp)
        ) {
            Canvas(modifier = Modifier.fillMaxSize()) {
                val strokeWidth = 14.dp.toPx()
                val radius = size.width / 2 - strokeWidth
                val center = Offset(size.width / 2, size.height)

                val colors = listOf(
                    Color(0xFFF5222D), // Extreme Fear (Red)
                    Color(0xFFFA8C16), // Fear (Orange)
                    Color(0xFFFADB14), // Neutral (Yellow)
                    Color(0xFF73D13D), // Greed (Lime)
                    Color(0xFF52C41A)  // Extreme Greed (Green)
                )

                val sweepPerSegment = 180f / colors.size
                colors.forEachIndexed { i, color ->
                    drawArc(
                        color = color,
                        startAngle = 180f + i * sweepPerSegment,
                        sweepAngle = sweepPerSegment - 1.5f,
                        useCenter = false,
                        topLeft = Offset(center.x - radius, center.y - radius),
                        size = Size(radius * 2, radius * 2),
                        style = Stroke(width = strokeWidth, cap = StrokeCap.Butt)
                    )
                }

                // Needle pointer
                val angleDeg = 180f + (animatedScore / 100f) * 180f
                val angleRad = Math.toRadians(angleDeg.toDouble())
                val needleLength = radius * 0.75f
                val needleEnd = Offset(
                    (center.x + needleLength * cos(angleRad)).toFloat(),
                    (center.y + needleLength * sin(angleRad)).toFloat()
                )

                drawLine(
                    color = textColor,
                    start = center,
                    end = needleEnd,
                    strokeWidth = 3.dp.toPx(),
                    cap = StrokeCap.Round
                )

                drawCircle(
                    color = textColor,
                    radius = 6.dp.toPx(),
                    center = center
                )
            }
        }

        Spacer(modifier = Modifier.height(10.dp))
        Text(
            text = "$score",
            fontSize = 36.sp,
            fontWeight = FontWeight.Bold,
            color = SemanticPositive
        )
        Text(
            text = label,
            fontSize = 15.sp,
            fontWeight = FontWeight.SemiBold,
            color = SemanticPositive
        )
    }
}
