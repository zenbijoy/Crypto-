package com.example.ui.screens

import androidx.compose.animation.AnimatedContent
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.togetherWith
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.*
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.R
import com.example.ui.viewmodel.CryptoScopeViewModel
import com.example.ui.viewmodel.ScreenRoute

@Composable
fun OnboardingScreen(viewModel: CryptoScopeViewModel) {
    var currentPage by remember { mutableIntStateOf(0) }

    val pageTitles = listOf(
        Pair("AI-Powered", "Market Intelligence"),
        Pair("Live Futures", "Order Flow Microstructure"),
        Pair("Institutional", "Risk-First Intelligence")
    )

    val pageSubtitles = listOf(
        "Track market trends, derivatives, liquidations,\nand order flow with clear insights\nand smarter crypto decisions.",
        "Inspect aggregated real-time order books,\nfunding rate heatmaps, and institutional CVD\nacross global crypto exchanges.",
        "Calibrated probabilistic forecast bounds (P10-P90)\nwith autonomous risk guard and rigorous\nNO-TRADE preservation discipline."
    )

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFFFFFFFF))
            .verticalScroll(rememberScrollState())
            .padding(bottom = 28.dp)
            .testTag("onboarding_screen"),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.SpaceBetween
    ) {
        Column(
            modifier = Modifier.fillMaxWidth(),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            // Top Bar with Skip action
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 24.dp, vertical = 12.dp),
                horizontalArrangement = Arrangement.End,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "Skip",
                    fontSize = 15.sp,
                    fontWeight = FontWeight.Medium,
                    color = Color(0xFF334155),
                    modifier = Modifier
                        .clickable(
                            interactionSource = remember { MutableInteractionSource() },
                            indication = null
                        ) {
                            viewModel.navigateTo(ScreenRoute.SIGN_IN)
                        }
                        .padding(horizontal = 8.dp, vertical = 6.dp)
                        .testTag("onboarding_skip_button")
                )
            }

            // Hero Illustration Graphic (3D floating cards, chart, coins, telescope lens)
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp)
                    .heightIn(min = 260.dp, max = 340.dp),
                contentAlignment = Alignment.Center
            ) {
                Image(
                    painter = painterResource(id = R.drawable.onboarding_hero),
                    contentDescription = "CryptoScope AI Hero",
                    modifier = Modifier
                        .fillMaxWidth()
                        .aspectRatio(941f / 880f),
                    contentScale = ContentScale.Fit
                )
            }

            Spacer(modifier = Modifier.height(12.dp))

            // Animated Typography Title and Subtitle
            AnimatedContent(
                targetState = currentPage,
                transitionSpec = { fadeIn() togetherWith fadeOut() },
                label = "onboarding_content"
            ) { page ->
                val (line1, line2) = pageTitles[page]
                Column(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(
                        text = line1,
                        fontSize = 28.sp,
                        fontWeight = FontWeight.ExtraBold,
                        color = Color(0xFF0F172A),
                        textAlign = TextAlign.Center,
                        letterSpacing = (-0.5).sp
                    )
                    Spacer(modifier = Modifier.height(2.dp))
                    Text(
                        text = line2,
                        fontSize = 28.sp,
                        fontWeight = FontWeight.ExtraBold,
                        style = TextStyle(
                            brush = Brush.horizontalGradient(
                                listOf(
                                    Color(0xFF00D2FF),
                                    Color(0xFF7C3AED),
                                    Color(0xFF9D00FF)
                                )
                            )
                        ),
                        textAlign = TextAlign.Center,
                        letterSpacing = (-0.5).sp
                    )

                    Spacer(modifier = Modifier.height(10.dp))

                    Text(
                        text = pageSubtitles[page],
                        fontSize = 13.5.sp,
                        lineHeight = 19.sp,
                        color = Color(0xFF64748B),
                        textAlign = TextAlign.Center,
                        modifier = Modifier.padding(horizontal = 32.dp)
                    )
                }
            }

            Spacer(modifier = Modifier.height(26.dp))

            // 4 Circular Feature Icons (Predictions, Order Flow, Liquidations, On-Chain)
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 20.dp),
                horizontalArrangement = Arrangement.SpaceEvenly,
                verticalAlignment = Alignment.Top
            ) {
                FeaturePill(
                    title = "Predictions",
                    icon = { PredictionsIcon() }
                )
                FeaturePill(
                    title = "Order Flow",
                    icon = { OrderFlowIcon() }
                )
                FeaturePill(
                    title = "Liquidations",
                    icon = { LiquidationsIcon() }
                )
                FeaturePill(
                    title = "On-Chain",
                    icon = { OnChainIcon() }
                )
            }
        }

        Spacer(modifier = Modifier.height(28.dp))

        // Bottom Controls: Pagination Dots + Gradient CTA Button
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 24.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            // 3-dot Carousel Indicator
            Row(
                horizontalArrangement = Arrangement.Center,
                verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier.padding(bottom = 20.dp)
            ) {
                repeat(3) { index ->
                    val isActive = index == currentPage
                    Box(
                        modifier = Modifier
                            .padding(horizontal = 4.dp)
                            .height(6.dp)
                            .width(if (isActive) 18.dp else 6.dp)
                            .clip(CircleShape)
                            .background(
                                if (isActive) Color(0xFF00D2FF) else Color(0xFFCBD5E1)
                            )
                    )
                }
            }

            // Gradient "Next" Pill Button
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(54.dp)
                    .shadow(
                        elevation = 8.dp,
                        shape = RoundedCornerShape(27.dp),
                        ambientColor = Color(0xFF00D2FF).copy(alpha = 0.35f),
                        spotColor = Color(0xFF9D00FF).copy(alpha = 0.45f)
                    )
                    .clip(RoundedCornerShape(27.dp))
                    .background(
                        Brush.horizontalGradient(
                            listOf(
                                Color(0xFF00E5FF),
                                Color(0xFF38BDF8),
                                Color(0xFF8B5CF6),
                                Color(0xFF9D00FF)
                            )
                        )
                    )
                    .clickable {
                        if (currentPage < 2) {
                            currentPage++
                        } else {
                            viewModel.navigateTo(ScreenRoute.SIGN_IN)
                        }
                    }
                    .testTag("onboarding_continue_button"),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = if (currentPage == 2) "Get Started" else "Next",
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color.White,
                    letterSpacing = 0.3.sp
                )
            }
        }
    }
}

@Composable
private fun FeaturePill(
    title: String,
    icon: @Composable () -> Unit
) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        modifier = Modifier.width(74.dp)
    ) {
        Box(
            modifier = Modifier
                .size(54.dp)
                .shadow(elevation = 2.dp, shape = CircleShape, spotColor = Color(0x1A000000))
                .clip(CircleShape)
                .background(
                    Brush.verticalGradient(
                        listOf(Color(0xFFFFFFFF), Color(0xFFF8FAFC))
                    )
                )
                .border(1.dp, Color(0xFFE2E8F0), CircleShape),
            contentAlignment = Alignment.Center
        ) {
            icon()
        }
        Spacer(modifier = Modifier.height(8.dp))
        Text(
            text = title,
            fontSize = 11.5.sp,
            fontWeight = FontWeight.Medium,
            color = Color(0xFF1E293B),
            textAlign = TextAlign.Center,
            maxLines = 1
        )
    }
}

@Composable
private fun PredictionsIcon() {
    Canvas(modifier = Modifier.size(24.dp)) {
        val stroke = 2.2.dp.toPx()
        val color = Color(0xFF0284C7)

        // Box base lines
        val boxPath = Path().apply {
            moveTo(size.width * 0.12f, size.height * 0.32f)
            lineTo(size.width * 0.12f, size.height * 0.85f)
            lineTo(size.width * 0.88f, size.height * 0.85f)
        }
        drawPath(
            boxPath,
            color.copy(alpha = 0.5f),
            style = Stroke(width = 1.8.dp.toPx(), cap = StrokeCap.Round, join = StrokeJoin.Round)
        )

        // Trend line
        val linePath = Path().apply {
            moveTo(size.width * 0.18f, size.height * 0.72f)
            lineTo(size.width * 0.44f, size.height * 0.38f)
            lineTo(size.width * 0.62f, size.height * 0.54f)
            lineTo(size.width * 0.86f, size.height * 0.24f)
        }
        drawPath(
            linePath,
            color,
            style = Stroke(width = stroke, cap = StrokeCap.Round, join = StrokeJoin.Round)
        )

        // Arrow head
        val arrow = Path().apply {
            moveTo(size.width * 0.66f, size.height * 0.24f)
            lineTo(size.width * 0.86f, size.height * 0.24f)
            lineTo(size.width * 0.86f, size.height * 0.44f)
        }
        drawPath(
            arrow,
            color,
            style = Stroke(width = stroke, cap = StrokeCap.Round, join = StrokeJoin.Round)
        )
    }
}

@Composable
private fun OrderFlowIcon() {
    Canvas(modifier = Modifier.size(24.dp)) {
        val stroke = 2.2.dp.toPx()
        val color = Color(0xFF7C3AED)

        // Line 1
        drawLine(
            color = color,
            start = Offset(size.width * 0.15f, size.height * 0.25f),
            end = Offset(size.width * 0.85f, size.height * 0.25f),
            strokeWidth = stroke,
            cap = StrokeCap.Round
        )
        drawCircle(color, radius = 2.8.dp.toPx(), center = Offset(size.width * 0.65f, size.height * 0.25f))

        // Line 2
        drawLine(
            color = color,
            start = Offset(size.width * 0.15f, size.height * 0.50f),
            end = Offset(size.width * 0.85f, size.height * 0.50f),
            strokeWidth = stroke,
            cap = StrokeCap.Round
        )
        drawCircle(color, radius = 2.8.dp.toPx(), center = Offset(size.width * 0.35f, size.height * 0.50f))

        // Line 3
        drawLine(
            color = color,
            start = Offset(size.width * 0.15f, size.height * 0.75f),
            end = Offset(size.width * 0.85f, size.height * 0.75f),
            strokeWidth = stroke,
            cap = StrokeCap.Round
        )
        drawCircle(color, radius = 2.8.dp.toPx(), center = Offset(size.width * 0.75f, size.height * 0.75f))
    }
}

@Composable
private fun LiquidationsIcon() {
    Canvas(modifier = Modifier.size(24.dp)) {
        val stroke = 2.2.dp.toPx()
        val color = Color(0xFF9333EA)

        // Downward Arrow 1
        drawLine(
            color = color,
            start = Offset(size.width * 0.26f, size.height * 0.18f),
            end = Offset(size.width * 0.26f, size.height * 0.80f),
            strokeWidth = stroke,
            cap = StrokeCap.Round
        )
        val arrow1 = Path().apply {
            moveTo(size.width * 0.14f, size.height * 0.62f)
            lineTo(size.width * 0.26f, size.height * 0.82f)
            lineTo(size.width * 0.38f, size.height * 0.62f)
        }
        drawPath(arrow1, color, style = Stroke(width = stroke, cap = StrokeCap.Round, join = StrokeJoin.Round))

        // Downward Arrow 2
        drawLine(
            color = color,
            start = Offset(size.width * 0.50f, size.height * 0.22f),
            end = Offset(size.width * 0.50f, size.height * 0.62f),
            strokeWidth = stroke,
            cap = StrokeCap.Round
        )
        val arrow2 = Path().apply {
            moveTo(size.width * 0.40f, size.height * 0.48f)
            lineTo(size.width * 0.50f, size.height * 0.64f)
            lineTo(size.width * 0.60f, size.height * 0.48f)
        }
        drawPath(arrow2, color, style = Stroke(width = stroke, cap = StrokeCap.Round, join = StrokeJoin.Round))

        // Warning Triangle badge
        val triColor = Color(0xFF7C3AED)
        val tri = Path().apply {
            moveTo(size.width * 0.82f, size.height * 0.50f)
            lineTo(size.width * 0.96f, size.height * 0.82f)
            lineTo(size.width * 0.68f, size.height * 0.82f)
            close()
        }
        drawPath(tri, triColor)
    }
}

@Composable
private fun OnChainIcon() {
    Canvas(modifier = Modifier.size(24.dp)) {
        val stroke = 1.8.dp.toPx()
        val color = Color(0xFF0284C7)
        val cx = size.width * 0.5f
        val cy = size.height * 0.5f
        val r = size.width * 0.36f

        // Isometric hexagon outline
        val path = Path().apply {
            moveTo(cx, cy - r)
            lineTo(cx + r * 0.866f, cy - r * 0.5f)
            lineTo(cx + r * 0.866f, cy + r * 0.5f)
            lineTo(cx, cy + r)
            lineTo(cx - r * 0.866f, cy + r * 0.5f)
            lineTo(cx - r * 0.866f, cy - r * 0.5f)
            close()
        }
        drawPath(path, color, style = Stroke(width = stroke, cap = StrokeCap.Round, join = StrokeJoin.Round))

        // Inner isometric lines connecting to center
        drawLine(color, Offset(cx, cy), Offset(cx, cy - r), strokeWidth = stroke, cap = StrokeCap.Round)
        drawLine(color, Offset(cx, cy), Offset(cx + r * 0.866f, cy + r * 0.5f), strokeWidth = stroke, cap = StrokeCap.Round)
        drawLine(color, Offset(cx, cy), Offset(cx - r * 0.866f, cy + r * 0.5f), strokeWidth = stroke, cap = StrokeCap.Round)

        // Center glowing node
        drawCircle(Color(0xFF00D2FF), radius = 2.4.dp.toPx(), center = Offset(cx, cy))
    }
}

