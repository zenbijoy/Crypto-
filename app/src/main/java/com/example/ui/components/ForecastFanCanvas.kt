package com.example.ui.components

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.*
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.core.model.CandleStick
import com.example.core.model.PredictionForecast
import com.example.ui.theme.*

@Composable
fun ForecastFanChart(
    candles: List<CandleStick>,
    prediction: PredictionForecast?,
    modifier: Modifier = Modifier,
    showForecastFan: Boolean = true,
    showSupportResistance: Boolean = true
) {
    var selectedCandleIndex by remember { mutableStateOf<Int?>(null) }

    Box(
        modifier = modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(BackgroundDark)
            .testTag("forecast_fan_chart")
    ) {
        Canvas(
            modifier = Modifier
                .fillMaxSize()
                .pointerInput(candles) {
                    detectTapGestures { offset ->
                        val candleWidth = size.width / (candles.size + if (showForecastFan) 8 else 1)
                        val idx = (offset.x / candleWidth).toInt().coerceIn(0, candles.size - 1)
                        selectedCandleIndex = if (selectedCandleIndex == idx) null else idx
                    }
                }
        ) {
            if (candles.isEmpty()) return@Canvas

            val chartWidth = size.width
            val chartHeight = size.height * 0.78f
            val volumeHeight = size.height * 0.20f
            val volumeTop = size.height * 0.80f

            // Price bounds
            var minPrice = candles.minOf { it.low }
            var maxPrice = candles.maxOf { it.high }

            if (prediction != null && showForecastFan) {
                minPrice = minOf(minPrice, prediction.p10)
                maxPrice = maxOf(maxPrice, prediction.p90)
            }

            val priceRange = if (maxPrice == minPrice) 1.0 else maxPrice - minPrice
            val maxVolume = candles.maxOfOrNull { it.volume } ?: 1.0

            val totalSlots = candles.size + (if (showForecastFan) 8 else 0)
            val slotWidth = chartWidth / totalSlots
            val candleBarWidth = slotWidth * 0.65f

            // 1. Draw horizontal grid lines
            for (i in 1..4) {
                val gridY = (chartHeight / 4) * i
                drawLine(
                    color = BorderColor.copy(alpha = 0.5f),
                    start = Offset(0f, gridY),
                    end = Offset(chartWidth, gridY),
                    strokeWidth = 1.dp.toPx()
                )
            }

            // 2. Draw Candlesticks & Volume
            candles.forEachIndexed { index, candle ->
                val xCenter = (index * slotWidth) + (slotWidth / 2)
                val isBull = candle.close >= candle.open
                val candleColor = if (isBull) SemanticPositive else SemanticNegative

                val yHigh = chartHeight - ((candle.high - minPrice) / priceRange * chartHeight).toFloat()
                val yLow = chartHeight - ((candle.low - minPrice) / priceRange * chartHeight).toFloat()
                val yOpen = chartHeight - ((candle.open - minPrice) / priceRange * chartHeight).toFloat()
                val yClose = chartHeight - ((candle.close - minPrice) / priceRange * chartHeight).toFloat()

                // Draw Wick
                drawLine(
                    color = candleColor,
                    start = Offset(xCenter, yHigh),
                    end = Offset(xCenter, yLow),
                    strokeWidth = 1.5.dp.toPx()
                )

                // Draw Candle Body
                val bodyTop = minOf(yOpen, yClose)
                val bodyBottom = maxOf(yOpen, yClose)
                val bodyHeight = maxOf(2f, bodyBottom - bodyTop)

                drawRect(
                    color = candleColor,
                    topLeft = Offset(xCenter - (candleBarWidth / 2), bodyTop),
                    size = Size(candleBarWidth, bodyHeight)
                )

                // Draw Volume Bar
                val vBarHeight = ((candle.volume / maxVolume) * volumeHeight).toFloat()
                drawRect(
                    color = candleColor.copy(alpha = 0.35f),
                    topLeft = Offset(xCenter - (candleBarWidth / 2), size.height - vBarHeight),
                    size = Size(candleBarWidth, vBarHeight)
                )
            }

            // 3. Draw Widening Forecast Fan
            if (prediction != null && showForecastFan && candles.isNotEmpty()) {
                val lastCandle = candles.last()
                val startX = ((candles.size - 1) * slotWidth) + (slotWidth / 2)
                val startY = chartHeight - ((lastCandle.close - minPrice) / priceRange * chartHeight).toFloat()

                val endX = chartWidth - (slotWidth / 2)
                val yP10 = chartHeight - ((prediction.p10 - minPrice) / priceRange * chartHeight).toFloat()
                val yP25 = chartHeight - ((prediction.p25 - minPrice) / priceRange * chartHeight).toFloat()
                val yP50 = chartHeight - ((prediction.p50 - minPrice) / priceRange * chartHeight).toFloat()
                val yP75 = chartHeight - ((prediction.p75 - minPrice) / priceRange * chartHeight).toFloat()
                val yP90 = chartHeight - ((prediction.p90 - minPrice) / priceRange * chartHeight).toFloat()

                // Outer fan cone (P10 - P90)
                val outerFanPath = Path().apply {
                    moveTo(startX, startY)
                    lineTo(endX, yP90)
                    lineTo(endX, yP10)
                    close()
                }
                drawPath(
                    path = outerFanPath,
                    brush = Brush.horizontalGradient(
                        colors = listOf(BrandGold.copy(alpha = 0.05f), BrandGold.copy(alpha = 0.18f)),
                        startX = startX,
                        endX = endX
                    )
                )

                // Inner fan cone (P25 - P75)
                val innerFanPath = Path().apply {
                    moveTo(startX, startY)
                    lineTo(endX, yP75)
                    lineTo(endX, yP25)
                    close()
                }
                drawPath(
                    path = innerFanPath,
                    brush = Brush.horizontalGradient(
                        colors = listOf(BrandGold.copy(alpha = 0.1f), BrandGold.copy(alpha = 0.32f)),
                        startX = startX,
                        endX = endX
                    )
                )

                // Forecast Fan Edge Lines
                drawLine(
                    color = BrandGold.copy(alpha = 0.6f),
                    start = Offset(startX, startY),
                    end = Offset(endX, yP90),
                    strokeWidth = 1.dp.toPx(),
                    pathEffect = PathEffect.dashPathEffect(floatArrayOf(8f, 6f))
                )
                drawLine(
                    color = BrandGold.copy(alpha = 0.6f),
                    start = Offset(startX, startY),
                    end = Offset(endX, yP10),
                    strokeWidth = 1.dp.toPx(),
                    pathEffect = PathEffect.dashPathEffect(floatArrayOf(8f, 6f))
                )

                // P50 Median expected path
                drawLine(
                    color = BrandGold,
                    start = Offset(startX, startY),
                    end = Offset(endX, yP50),
                    strokeWidth = 2.dp.toPx()
                )

                // Median destination node
                drawCircle(
                    color = BrandGold,
                    radius = 4.dp.toPx(),
                    center = Offset(endX, yP50)
                )
            }

            // 4. Crosshair for selected candle
            selectedCandleIndex?.let { selIdx ->
                if (selIdx in candles.indices) {
                    val selCandle = candles[selIdx]
                    val selX = (selIdx * slotWidth) + (slotWidth / 2)
                    val selY = chartHeight - ((selCandle.close - minPrice) / priceRange * chartHeight).toFloat()

                    drawLine(
                        color = TextPrimary.copy(alpha = 0.6f),
                        start = Offset(selX, 0f),
                        end = Offset(selX, size.height),
                        strokeWidth = 1.dp.toPx(),
                        pathEffect = PathEffect.dashPathEffect(floatArrayOf(6f, 6f))
                    )
                    drawLine(
                        color = TextPrimary.copy(alpha = 0.6f),
                        start = Offset(0f, selY),
                        end = Offset(chartWidth, selY),
                        strokeWidth = 1.dp.toPx(),
                        pathEffect = PathEffect.dashPathEffect(floatArrayOf(6f, 6f))
                    )
                }
            }
        }

        // Overlay Badge for Selected Candle or Legend
        val selIdx = selectedCandleIndex
        if (selIdx != null && selIdx in candles.indices) {
            val candle = candles[selIdx]
            Surface(
                shape = RoundedCornerShape(6.dp),
                color = SurfaceRaised.copy(alpha = 0.9f),
                border = BorderStroke(1.dp, BorderColor),
                modifier = Modifier
                    .align(Alignment.TopStart)
                    .padding(8.dp)
            ) {
                Row(
                    modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Text("O: $${String.format("%.1f", candle.open)}", fontSize = 10.sp, color = TextMuted)
                    Text("H: $${String.format("%.1f", candle.high)}", fontSize = 10.sp, color = TextMuted)
                    Text("L: $${String.format("%.1f", candle.low)}", fontSize = 10.sp, color = TextMuted)
                    Text("C: $${String.format("%.1f", candle.close)}", fontSize = 10.sp, fontWeight = FontWeight.Bold, color = if (candle.close >= candle.open) SemanticPositive else SemanticNegative)
                }
            }
        }
    }
}
