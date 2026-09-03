package com.example.ui.screens

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Close
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.ui.theme.*
import com.example.ui.viewmodel.CryptoScopeViewModel

@Composable
fun PaperPositionDetailScreen(viewModel: CryptoScopeViewModel) {
    val uiState by viewModel.uiState.collectAsState()
    val isDark = uiState.isDarkTheme
    val bgColor = if (isDark) DarkBackground else LightBackground
    val cardColor = if (isDark) DarkSurface else LightSurface
    val borderColor = if (isDark) DarkBorder else LightBorder
    val textColor = if (isDark) DarkTextPrimary else LightTextPrimary
    val textMutedColor = if (isDark) DarkTextMuted else LightTextMuted

    val positions by viewModel.repository.getPaperPositions().collectAsState(initial = emptyList())
    val position = positions.firstOrNull { it.id == uiState.activePositionDetailId } ?: positions.firstOrNull()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(bgColor)
            .padding(horizontal = 16.dp)
            .verticalScroll(rememberScrollState())
            .testTag("paper_position_detail_screen")
    ) {
        Spacer(modifier = Modifier.height(12.dp))

        // Top App Bar
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            IconButton(onClick = { viewModel.navigateBack() }, modifier = Modifier.size(32.dp)) {
                Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back", tint = textColor)
            }
            Spacer(modifier = Modifier.width(6.dp))
            Column {
                Text(
                    text = "${position?.symbol ?: "BTC/USDT"} Position",
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold,
                    color = textColor
                )
                Text(
                    text = "Paper Execution • Gated",
                    fontSize = 10.sp,
                    color = textMutedColor
                )
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        if (position != null) {
            val isLong = position.direction == "LONG"
            val pnlUsd = if (position.entryPrice > 0) (position.markPrice - position.entryPrice) * (position.sizeUsd / position.entryPrice) * (if (isLong) 1 else -1) else 0.0
            val pnlPct = if (position.entryPrice > 0) ((position.markPrice - position.entryPrice) / position.entryPrice) * 100.0 * (if (isLong) 1 else -1) else 0.0
            val isPos = pnlUsd >= 0
            val pnlColor = if (isPos) SemanticPositive else SemanticNegative

            // Hero PnL Card
            Surface(
                shape = RoundedCornerShape(16.dp),
                color = cardColor,
                border = BorderStroke(1.dp, borderColor),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(18.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Surface(
                            shape = RoundedCornerShape(4.dp),
                            color = if (isLong) SemanticPositiveLight else SemanticNegativeLight
                        ) {
                            Text(
                                text = position.direction,
                                fontSize = 11.sp,
                                fontWeight = FontWeight.Bold,
                                color = if (isLong) SemanticPositive else SemanticNegative,
                                modifier = Modifier.padding(horizontal = 8.dp, vertical = 2.dp)
                            )
                        }
                        Text(
                            text = "Size: $${String.format("%,.2f", position.sizeUsd)}",
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Medium,
                            color = textMutedColor
                        )
                    }

                    Spacer(modifier = Modifier.height(14.dp))

                    Text(
                        text = "UNREALIZED PnL",
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Bold,
                        color = textMutedColor
                    )
                    Spacer(modifier = Modifier.height(2.dp))
                    Text(
                        text = "${if (isPos) "+" else ""}$${String.format("%,.2f", pnlUsd)} (${String.format("%+.2f", pnlPct)}%)",
                        fontSize = 24.sp,
                        fontWeight = FontWeight.Bold,
                        color = pnlColor
                    )
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            // Position Execution Telemetry Card
            Surface(
                shape = RoundedCornerShape(14.dp),
                color = cardColor,
                border = BorderStroke(1.dp, borderColor),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(
                        text = "POSITION PARAMETERS",
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Bold,
                        color = textMutedColor,
                        letterSpacing = 0.8.sp
                    )
                    Spacer(modifier = Modifier.height(12.dp))

                    DetailRow("Entry Price", "$${String.format("%,.2f", position.entryPrice)}", textColor, textMutedColor)
                    DetailRow("Mark Price", "$${String.format("%,.2f", position.markPrice)}", textColor, textMutedColor)
                    DetailRow("Estimated Liq Price", "$${String.format("%,.2f", position.entryPrice * 0.75)}", textColor, textMutedColor)
                    DetailRow("Stop Loss", "$${String.format("%,.2f", position.stopLoss)}", textColor, textMutedColor)
                    DetailRow("Take Profit", "$${String.format("%,.2f", position.takeProfit)}", textColor, textMutedColor)
                    DetailRow("AI Confidence at Entry", "${position.aiConfidence}%", textColor, textMutedColor)
                    DetailRow("AI Regime Trigger", position.aiRegime, textColor, textMutedColor)
                    DetailRow("Model Version", position.aiModel, textColor, textMutedColor)
                }
            }

            Spacer(modifier = Modifier.height(24.dp))

            // Action Buttons
            Button(
                onClick = { viewModel.closePaperPosition(position.id) },
                colors = ButtonDefaults.buttonColors(
                    containerColor = SemanticNegativeLight,
                    contentColor = SemanticNegative
                ),
                border = BorderStroke(1.dp, SemanticNegative),
                shape = RoundedCornerShape(10.dp),
                modifier = Modifier
                    .fillMaxWidth()
                    .height(48.dp)
                    .testTag("close_position_button")
            ) {
                Icon(Icons.Default.Close, contentDescription = null, modifier = Modifier.size(16.dp))
                Spacer(modifier = Modifier.width(6.dp))
                Text("MARKET CLOSE POSITION", fontSize = 13.sp, fontWeight = FontWeight.Bold)
            }
        }
    }
}

@Composable
private fun DetailRow(label: String, value: String, textColor: Color, textMutedColor: Color) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 5.dp),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(text = label, fontSize = 12.sp, color = textMutedColor)
        Text(text = value, fontSize = 12.sp, fontWeight = FontWeight.SemiBold, color = textColor)
    }
}

