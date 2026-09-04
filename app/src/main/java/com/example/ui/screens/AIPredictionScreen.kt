package com.example.ui.screens

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
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
import com.example.core.model.*
import com.example.ui.components.*
import com.example.ui.theme.*
import com.example.ui.viewmodel.CryptoScopeViewModel
import com.example.ui.viewmodel.ScreenRoute

@Composable
fun AIPredictionScreen(viewModel: CryptoScopeViewModel) {
    val uiState by viewModel.uiState.collectAsState()
    val isDark = uiState.isDarkTheme
    val bgColor = if (isDark) DarkBackground else LightBackground
    val cardColor = if (isDark) DarkSurface else LightSurface
    val borderColor = if (isDark) DarkBorder else LightBorder
    val textColor = if (isDark) DarkTextPrimary else LightTextPrimary
    val textMutedColor = if (isDark) DarkTextMuted else LightTextMuted

    val livePrices by viewModel.repository.livePrices.collectAsState()
    val prediction = remember(livePrices, uiState.selectedAsset, uiState.selectedHorizon) {
        viewModel.repository.getPrediction(uiState.selectedAsset, uiState.selectedHorizon)
    }
    val candles = remember(uiState.selectedAsset) {
        viewModel.repository.getCandles(uiState.selectedAsset, 24)
    }

    val horizons = listOf(
        Horizon.H_1M,
        Horizon.H_5M,
        Horizon.H_15M,
        Horizon.H_30M,
        Horizon.H_1H,
        Horizon.H_4H,
        Horizon.H_12H,
        Horizon.H_1D,
        Horizon.H_3D,
        Horizon.H_7D
    )

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(bgColor)
            .padding(horizontal = 16.dp)
            .verticalScroll(rememberScrollState())
            .testTag("ai_prediction_screen")
    ) {
        Spacer(modifier = Modifier.height(12.dp))

        // Header: Asset, Tier, Data Quality, Audit link
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    text = "${uiState.selectedAsset.name}/USDT",
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold,
                    color = textColor
                )
                Spacer(modifier = Modifier.width(8.dp))
                Surface(
                    shape = RoundedCornerShape(12.dp),
                    color = if (isDark) BrandBlue.copy(alpha = 0.2f) else BrandBlueLight,
                    border = BorderStroke(1.dp, BrandBlue.copy(alpha = 0.3f))
                ) {
                    Text(
                        text = prediction.modelTier.uppercase(),
                        fontSize = 9.sp,
                        fontWeight = FontWeight.Bold,
                        color = BrandBlue,
                        modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                    )
                }
            }

            Row(verticalAlignment = Alignment.CenterVertically) {
                DataQualityChip(score = prediction.dataQualityScore)
                Spacer(modifier = Modifier.width(8.dp))
                IconButton(
                    onClick = { viewModel.navigateTo(ScreenRoute.PREDICTION_HISTORY) },
                    modifier = Modifier.size(28.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.History,
                        contentDescription = "Audit History",
                        tint = BrandBlue,
                        modifier = Modifier.size(18.dp)
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(10.dp))

        // Multi-Asset Quick Switcher Row
        LazyRow(
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            modifier = Modifier.fillMaxWidth()
        ) {
            items(AssetSymbol.values()) { asset ->
                val isSelected = uiState.selectedAsset == asset
                val assetPrice = livePrices[asset.code] ?: asset.basePrice
                Surface(
                    shape = RoundedCornerShape(16.dp),
                    color = if (isSelected) BrandBlue else (if (isDark) DarkSurfaceRaised else LightSurfaceRaised),
                    border = BorderStroke(1.dp, if (isSelected) BrandBlue else borderColor),
                    modifier = Modifier.clickable { viewModel.selectAsset(asset) }
                ) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        modifier = Modifier.padding(horizontal = 10.dp, vertical = 5.dp)
                    ) {
                        Text(
                            text = asset.name,
                            fontSize = 11.sp,
                            fontWeight = FontWeight.Bold,
                            color = if (isSelected) Color.White else textColor
                        )
                        Spacer(modifier = Modifier.width(4.dp))
                        Text(
                            text = "$${if (assetPrice >= 1000) String.format("%,.0f", assetPrice) else String.format("%.2f", assetPrice)}",
                            fontSize = 10.sp,
                            color = if (isSelected) Color.White.copy(alpha = 0.85f) else textMutedColor
                        )
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(10.dp))

        // Multi-Horizon Selector Pills (1m to 7d)
        LazyRow(
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            modifier = Modifier.fillMaxWidth()
        ) {
            items(horizons) { horizon ->
                val isSelected = uiState.selectedHorizon == horizon
                Surface(
                    shape = RoundedCornerShape(16.dp),
                    color = if (isSelected) BrandBlue else (if (isDark) DarkSurfaceRaised else LightSurfaceRaised),
                    border = BorderStroke(1.dp, if (isSelected) BrandBlue else borderColor),
                    modifier = Modifier
                        .clickable { viewModel.selectHorizon(horizon) }
                        .testTag("horizon_${horizon.display}")
                ) {
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally,
                        modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp)
                    ) {
                        Text(
                            text = horizon.display,
                            fontSize = 12.sp,
                            fontWeight = if (isSelected) FontWeight.Bold else FontWeight.SemiBold,
                            color = if (isSelected) Color.White else textColor
                        )
                        Text(
                            text = horizon.description,
                            fontSize = 9.sp,
                            color = if (isSelected) Color.White.copy(alpha = 0.8f) else textMutedColor
                        )
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(14.dp))

        // Signal Abstention Engine Card (Institutional NO SIGNAL state)
        if (prediction.isAbstained || prediction.signal == SignalType.ABSTAINED) {
            Surface(
                shape = RoundedCornerShape(14.dp),
                color = WarningSurface,
                border = BorderStroke(1.dp, SemanticWarning.copy(alpha = 0.4f)),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(14.dp)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(
                            imageVector = Icons.Default.Shield,
                            contentDescription = null,
                            tint = SemanticWarning,
                            modifier = Modifier.size(20.dp)
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = "SIGNAL ABSTENTION ENGINE TRIGGERED",
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Bold,
                            color = SemanticWarning
                        )
                    }
                    Spacer(modifier = Modifier.height(6.dp))
                    Text(
                        text = prediction.abstainReason ?: "High uncertainty detected: Sub-model divergence (agreement < 60%) or unstable book depth. Engine refuses to emit false-certainty forecast.",
                        fontSize = 12.sp,
                        color = textColor,
                        lineHeight = 16.sp
                    )
                    Spacer(modifier = Modifier.height(6.dp))
                    Text(
                        text = "Statistically verified: Abstaining on low-edge regimes preserves capital and raises Sharpe ratio.",
                        fontSize = 10.sp,
                        color = textMutedColor
                    )
                }
            }
            Spacer(modifier = Modifier.height(14.dp))
        }

        // Hero Card: Confidence, Direction, Return, Quantile Range
        Surface(
            shape = RoundedCornerShape(16.dp),
            color = cardColor,
            border = BorderStroke(1.dp, borderColor),
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    // Confidence Ring Gauge
                    ConfidenceRing(
                        score = prediction.confidenceScore,
                        size = 80.dp
                    )

                    // Prediction Output Summary
                    Column(
                        modifier = Modifier
                            .weight(1f)
                            .padding(start = 14.dp)
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            SignalBadge(signal = prediction.signal)
                            Spacer(modifier = Modifier.width(6.dp))
                            RiskBadge(risk = prediction.riskLevel)
                        }

                        Spacer(modifier = Modifier.height(6.dp))

                        Text(
                            text = "${if (prediction.expectedReturnPct >= 0) "+" else ""}${prediction.expectedReturnPct}% Exp. Return",
                            fontSize = 18.sp,
                            fontWeight = FontWeight.Bold,
                            color = if (prediction.expectedReturnPct >= 0) SemanticPositive else SemanticNegative
                        )

                        Spacer(modifier = Modifier.height(2.dp))

                        Text(
                            text = "Expected range: $${String.format("%,.1f", prediction.p10)} – $${String.format("%,.1f", prediction.p90)}",
                            fontSize = 11.sp,
                            color = textMutedColor
                        )

                        Text(
                            text = "Ensemble Agreement: ${prediction.modelAgreementScore}%",
                            fontSize = 11.sp,
                            fontWeight = FontWeight.SemiBold,
                            color = BrandBlue
                        )
                    }
                }

                Spacer(modifier = Modifier.height(12.dp))
                HorizontalDivider(color = borderColor.copy(alpha = 0.5f))
                Spacer(modifier = Modifier.height(10.dp))

                // Regime & Volatility Metrics
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Column {
                        Text("MARKET REGIME", fontSize = 9.sp, fontWeight = FontWeight.Bold, color = textMutedColor)
                        Text(prediction.regime, fontSize = 11.sp, fontWeight = FontWeight.SemiBold, color = textColor)
                    }
                    Column(horizontalAlignment = Alignment.End) {
                        Text("EXPECTED VOLATILITY", fontSize = 9.sp, fontWeight = FontWeight.Bold, color = textMutedColor)
                        Text("±${prediction.expectedVolatilityPct}%", fontSize = 11.sp, fontWeight = FontWeight.SemiBold, color = textColor)
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(14.dp))

        // Direction Probability Triad
        Text(
            text = "Direction Probability Distribution",
            fontSize = 13.sp,
            fontWeight = FontWeight.Bold,
            color = textColor
        )
        Spacer(modifier = Modifier.height(6.dp))
        Surface(
            shape = RoundedCornerShape(14.dp),
            color = cardColor,
            border = BorderStroke(1.dp, borderColor),
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(modifier = Modifier.padding(14.dp)) {
                ProbabilityBar(
                    pUp = prediction.pUp,
                    pSideways = prediction.pSideways,
                    pDown = prediction.pDown
                )
                Spacer(modifier = Modifier.height(10.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text("P(Up): ${(prediction.pUp * 100).toInt()}%", fontSize = 11.sp, fontWeight = FontWeight.Bold, color = SemanticPositive)
                    Text("P(Neutral): ${(prediction.pSideways * 100).toInt()}%", fontSize = 11.sp, fontWeight = FontWeight.Bold, color = textMutedColor)
                    Text("P(Down): ${(prediction.pDown * 100).toInt()}%", fontSize = 11.sp, fontWeight = FontWeight.Bold, color = SemanticNegative)
                }
            }
        }

        Spacer(modifier = Modifier.height(14.dp))

        // Sub-Models Ensemble Breakdown Card
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
                    Text(
                        text = "Sub-Model Ensemble Matrix",
                        fontSize = 13.sp,
                        fontWeight = FontWeight.Bold,
                        color = textColor
                    )
                    Text(
                        text = "Agreement ${prediction.modelAgreementScore}%",
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Bold,
                        color = BrandBlue
                    )
                }

                Spacer(modifier = Modifier.height(10.dp))

                prediction.subModels.forEach { model ->
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(vertical = 4.dp),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Column(modifier = Modifier.weight(1f)) {
                            Text(
                                text = model.name,
                                fontSize = 11.sp,
                                fontWeight = FontWeight.SemiBold,
                                color = textColor
                            )
                            Text(
                                text = "Weight ${(model.weight * 100).toInt()}%",
                                fontSize = 9.sp,
                                color = textMutedColor
                            )
                        }

                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Text(
                                text = "${(model.bullishProb * 100).toInt()}% Bullish",
                                fontSize = 11.sp,
                                fontWeight = FontWeight.Bold,
                                color = if (model.bullishProb >= 0.65) SemanticPositive else (if (model.bullishProb <= 0.40) SemanticNegative else textMutedColor)
                            )
                            Spacer(modifier = Modifier.width(6.dp))
                            Surface(
                                shape = RoundedCornerShape(4.dp),
                                color = if (model.bullishProb >= 0.65) SemanticPositiveLight else (if (model.bullishProb <= 0.40) SemanticNegativeLight else if (isDark) DarkSurfaceRaised else LightSurfaceRaised)
                            ) {
                                Text(
                                    text = model.signal,
                                    fontSize = 8.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = if (model.bullishProb >= 0.65) SemanticPositive else (if (model.bullishProb <= 0.40) SemanticNegative else textMutedColor),
                                    modifier = Modifier.padding(horizontal = 4.dp, vertical = 2.dp)
                                )
                            }
                        }
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(14.dp))

        // Important Factors / Feature Attributions (SHAP weights)
        Surface(
            shape = RoundedCornerShape(14.dp),
            color = cardColor,
            border = BorderStroke(1.dp, borderColor),
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(modifier = Modifier.padding(14.dp)) {
                Text(
                    text = "Important Drivers & Feature Attributions",
                    fontSize = 13.sp,
                    fontWeight = FontWeight.Bold,
                    color = textColor
                )
                Spacer(modifier = Modifier.height(10.dp))
                prediction.attributions.forEach { attr ->
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(vertical = 3.dp),
                        verticalAlignment = Alignment.Top
                    ) {
                        Text(
                            text = if (attr.isBullish) "↑" else "↓",
                            fontSize = 14.sp,
                            fontWeight = FontWeight.Bold,
                            color = if (attr.isBullish) SemanticPositive else SemanticNegative
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Column {
                            Text(
                                text = attr.feature,
                                fontSize = 12.sp,
                                fontWeight = FontWeight.SemiBold,
                                color = textColor
                            )
                            Text(
                                text = attr.description,
                                fontSize = 10.sp,
                                color = textMutedColor,
                                lineHeight = 13.sp
                            )
                        }
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(14.dp))

        // Risk Warning Banner
        Surface(
            shape = RoundedCornerShape(12.dp),
            color = if (prediction.riskLevel == RiskLevel.HIGH) NegativeSurface else if (isDark) DarkSurfaceRaised else LightSurfaceRaised,
            border = BorderStroke(1.dp, if (prediction.riskLevel == RiskLevel.HIGH) SemanticNegative.copy(alpha = 0.3f) else borderColor),
            modifier = Modifier.fillMaxWidth()
        ) {
            Row(
                modifier = Modifier.padding(12.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(
                    imageVector = Icons.Default.WarningAmber,
                    contentDescription = null,
                    tint = if (prediction.riskLevel == RiskLevel.HIGH) SemanticNegative else BrandBlue,
                    modifier = Modifier.size(18.dp)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Column {
                    Text(
                        text = "RISK INTELLIGENCE",
                        fontSize = 9.sp,
                        fontWeight = FontWeight.Bold,
                        color = if (prediction.riskLevel == RiskLevel.HIGH) SemanticNegative else BrandBlue
                    )
                    Text(
                        text = prediction.riskWarning,
                        fontSize = 11.sp,
                        color = textColor,
                        lineHeight = 14.sp
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(14.dp))

        // Forecast Fan Chart (Quantile envelopes P10 - P90)
        Text(
            text = "Quantile Forecast Fan (${prediction.horizon.display})",
            fontSize = 13.sp,
            fontWeight = FontWeight.Bold,
            color = textColor
        )
        Spacer(modifier = Modifier.height(6.dp))
        ForecastFanChart(
            candles = candles,
            prediction = prediction,
            modifier = Modifier
                .fillMaxWidth()
                .height(200.dp),
            showForecastFan = true
        )

        Spacer(modifier = Modifier.height(16.dp))

        // Action CTAs
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            Button(
                onClick = { viewModel.navigateTo(ScreenRoute.PAPER_ORDER_TICKET) },
                colors = ButtonDefaults.buttonColors(containerColor = BrandBlue, contentColor = Color.White),
                shape = RoundedCornerShape(10.dp),
                modifier = Modifier
                    .weight(1f)
                    .height(46.dp)
                    .testTag("ai_paper_trade_button")
            ) {
                Text("SIMULATE PAPER TRADE", fontSize = 12.sp, fontWeight = FontWeight.Bold)
            }
            OutlinedButton(
                onClick = { viewModel.navigateTo(ScreenRoute.CREATE_ALERT) },
                colors = ButtonDefaults.outlinedButtonColors(contentColor = textColor),
                border = BorderStroke(1.dp, borderColor),
                shape = RoundedCornerShape(10.dp),
                modifier = Modifier
                    .weight(1f)
                    .height(46.dp)
                    .testTag("ai_create_alert_button")
            ) {
                Text("CREATE ALERT", fontSize = 12.sp, fontWeight = FontWeight.Bold)
            }
        }

        Spacer(modifier = Modifier.height(80.dp))
    }
}
