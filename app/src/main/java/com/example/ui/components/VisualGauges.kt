package com.example.ui.components

import androidx.compose.animation.core.*
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.*
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.core.model.*
import com.example.ui.theme.*

@Composable
fun ConfidenceRing(
    score: Int,
    modifier: Modifier = Modifier,
    size: Dp = 92.dp,
    strokeWidth: Dp = 7.dp
) {
    val animatedProgress by animateFloatAsState(
        targetValue = (score / 100f).coerceIn(0f, 1f),
        animationSpec = tween(durationMillis = 800, easing = FastOutSlowInEasing),
        label = "confidence_progress"
    )

    val arcColor = when {
        score >= 80 -> BrandGold
        score >= 65 -> SemanticPositive
        score >= 50 -> SemanticInfo
        else -> TextMuted
    }

    Box(
        contentAlignment = Alignment.Center,
        modifier = modifier
            .size(size)
            .testTag("confidence_ring")
    ) {
        Canvas(modifier = Modifier.fillMaxSize()) {
            val strokePx = strokeWidth.toPx()
            val arcSize = size.toPx() - strokePx
            val topLeft = Offset(strokePx / 2, strokePx / 2)

            // Background track
            drawArc(
                color = SurfaceRaised,
                startAngle = -90f,
                sweepAngle = 360f,
                useCenter = false,
                topLeft = topLeft,
                size = Size(arcSize, arcSize),
                style = Stroke(width = strokePx, cap = StrokeCap.Round)
            )

            // Active Arc
            drawArc(
                color = arcColor,
                startAngle = -90f,
                sweepAngle = animatedProgress * 360f,
                useCenter = false,
                topLeft = topLeft,
                size = Size(arcSize, arcSize),
                style = Stroke(width = strokePx, cap = StrokeCap.Round)
            )
        }

        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Text(
                text = "$score",
                fontSize = 24.sp,
                fontWeight = FontWeight.Bold,
                color = TextPrimary
            )
            Text(
                text = "CONF",
                fontSize = 9.sp,
                fontWeight = FontWeight.SemiBold,
                color = TextMuted,
                letterSpacing = 0.5.sp
            )
        }
    }
}

@Composable
fun ProbabilityBar(
    pUp: Double,
    pSideways: Double,
    pDown: Double,
    modifier: Modifier = Modifier
) {
    val upPct = (pUp * 100).toInt()
    val sidePct = (pSideways * 100).toInt()
    val downPct = (pDown * 100).toInt()

    Column(modifier = modifier.fillMaxWidth()) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .height(10.dp)
                .clip(RoundedCornerShape(5.dp))
                .background(SurfaceRaised)
        ) {
            if (pUp > 0) {
                Box(
                    modifier = Modifier
                        .fillMaxHeight()
                        .weight((pUp.toFloat() + 0.001f))
                        .background(SemanticPositive)
                )
            }
            if (pSideways > 0) {
                Box(
                    modifier = Modifier
                        .fillMaxHeight()
                        .weight((pSideways.toFloat() + 0.001f))
                        .background(TextMuted)
                )
            }
            if (pDown > 0) {
                Box(
                    modifier = Modifier
                        .fillMaxHeight()
                        .weight((pDown.toFloat() + 0.001f))
                        .background(SemanticNegative)
                )
            }
        }
        Spacer(modifier = Modifier.height(6.dp))
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Box(modifier = Modifier.size(6.dp).clip(CircleShape).background(SemanticPositive))
                Spacer(modifier = Modifier.width(4.dp))
                Text("UP $upPct%", fontSize = 11.sp, fontWeight = FontWeight.SemiBold, color = SemanticPositive)
            }
            Row(verticalAlignment = Alignment.CenterVertically) {
                Box(modifier = Modifier.size(6.dp).clip(CircleShape).background(TextMuted))
                Spacer(modifier = Modifier.width(4.dp))
                Text("SIDE $sidePct%", fontSize = 11.sp, fontWeight = FontWeight.SemiBold, color = TextMuted)
            }
            Row(verticalAlignment = Alignment.CenterVertically) {
                Box(modifier = Modifier.size(6.dp).clip(CircleShape).background(SemanticNegative))
                Spacer(modifier = Modifier.width(4.dp))
                Text("DOWN $downPct%", fontSize = 11.sp, fontWeight = FontWeight.SemiBold, color = SemanticNegative)
            }
        }
    }
}

@Composable
fun Sparkline(
    data: List<Double>,
    modifier: Modifier = Modifier,
    isPositive: Boolean = true
) {
    if (data.size < 2) return

    val strokeColor = if (isPositive) SemanticPositive else SemanticNegative
    val fillColor = if (isPositive) PositiveSurface else NegativeSurface

    Canvas(modifier = modifier) {
        val minVal = data.minOrNull() ?: 0.0
        val maxVal = data.maxOrNull() ?: 1.0
        val range = if (maxVal == minVal) 1.0 else maxVal - minVal

        val points = data.mapIndexed { index, value ->
            val x = index.toFloat() / (data.size - 1) * size.width
            val y = size.height - ((value - minVal) / range * size.height).toFloat()
            Offset(x, y.coerceIn(2f, size.height - 2f))
        }

        val path = Path().apply {
            moveTo(points.first().x, points.first().y)
            for (i in 1 until points.size) {
                lineTo(points[i].x, points[i].y)
            }
        }

        // Draw Line
        drawPath(
            path = path,
            color = strokeColor,
            style = Stroke(width = 2.dp.toPx(), cap = StrokeCap.Round, join = StrokeJoin.Round)
        )

        // Draw Gradient Fill under line
        val fillPath = Path().apply {
            addPath(path)
            lineTo(size.width, size.height)
            lineTo(0f, size.height)
            close()
        }
        drawPath(
            path = fillPath,
            brush = Brush.verticalGradient(
                colors = listOf(fillColor, Color.Transparent)
            )
        )
    }
}
