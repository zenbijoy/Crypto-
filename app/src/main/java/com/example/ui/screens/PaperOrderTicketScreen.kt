package com.example.ui.screens

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.ui.theme.*
import com.example.ui.viewmodel.CryptoScopeViewModel

@Composable
fun PaperOrderTicketScreen(viewModel: CryptoScopeViewModel) {
    val uiState by viewModel.uiState.collectAsState()
    val isDark = uiState.isDarkTheme
    val bgColor = if (isDark) DarkBackground else LightBackground
    val cardColor = if (isDark) DarkSurface else LightSurface
    val borderColor = if (isDark) DarkBorder else LightBorder
    val textColor = if (isDark) DarkTextPrimary else LightTextPrimary
    val textMutedColor = if (isDark) DarkTextMuted else LightTextMuted

    val livePrices by viewModel.repository.livePrices.collectAsState()
    val currentPrice = livePrices[uiState.selectedAsset.code] ?: uiState.selectedAsset.basePrice

    var side by remember { mutableStateOf("BUY") }
    var orderType by remember { mutableStateOf("MARKET") }
    var leverage by remember { mutableFloatStateOf(10f) }
    var sizeBtc by remember { mutableStateOf("0.10") }
    var takeProfit by remember { mutableStateOf(String.format("%.1f", currentPrice * 1.02)) }
    var stopLoss by remember { mutableStateOf(String.format("%.1f", currentPrice * 0.985)) }

    val sizeNum = sizeBtc.toDoubleOrNull() ?: 0.0
    val notionalUsd = sizeNum * currentPrice
    val marginRequired = notionalUsd / leverage
    val estFee = notionalUsd * 0.0004
    val estSlippage = notionalUsd * 0.0002

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(bgColor)
            .padding(horizontal = 16.dp)
            .verticalScroll(rememberScrollState())
            .testTag("paper_order_ticket_screen")
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
                Text("Paper Order Ticket", fontSize = 18.sp, fontWeight = FontWeight.Bold, color = textColor)
                Text("${uiState.selectedAsset.name}/USDT Perpetual", fontSize = 10.sp, color = textMutedColor)
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Buy / Sell Selector
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            Button(
                onClick = { side = "BUY" },
                colors = ButtonDefaults.buttonColors(
                    containerColor = if (side == "BUY") SemanticPositive else (if (isDark) DarkSurfaceRaised else LightSurfaceRaised),
                    contentColor = if (side == "BUY") Color.White else textMutedColor
                ),
                shape = RoundedCornerShape(10.dp),
                modifier = Modifier.weight(1f).height(42.dp)
            ) {
                Text("BUY / LONG", fontSize = 13.sp, fontWeight = FontWeight.Bold)
            }
            Button(
                onClick = { side = "SELL" },
                colors = ButtonDefaults.buttonColors(
                    containerColor = if (side == "SELL") SemanticNegative else (if (isDark) DarkSurfaceRaised else LightSurfaceRaised),
                    contentColor = if (side == "SELL") Color.White else textMutedColor
                ),
                shape = RoundedCornerShape(10.dp),
                modifier = Modifier.weight(1f).height(42.dp)
            ) {
                Text("SELL / SHORT", fontSize = 13.sp, fontWeight = FontWeight.Bold)
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Order Type selector
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            listOf("MARKET", "LIMIT", "CONDITIONAL").forEach { type ->
                val isSelected = orderType == type
                Surface(
                    shape = RoundedCornerShape(16.dp),
                    color = if (isSelected) BrandBlue else (if (isDark) DarkSurfaceRaised else LightSurfaceRaised),
                    border = BorderStroke(1.dp, if (isSelected) BrandBlue else borderColor),
                    modifier = Modifier.clickable { orderType = type }
                ) {
                    Text(
                        text = type,
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Bold,
                        color = if (isSelected) Color.White else textMutedColor,
                        modifier = Modifier.padding(horizontal = 14.dp, vertical = 6.dp)
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Leverage Slider
        Text("LEVERAGE: ${leverage.toInt()}X", fontSize = 11.sp, fontWeight = FontWeight.Bold, color = textMutedColor)
        Slider(
            value = leverage,
            onValueChange = { leverage = it },
            valueRange = 1f..50f,
            steps = 49,
            colors = SliderDefaults.colors(thumbColor = BrandBlue, activeTrackColor = BrandBlue)
        )

        Spacer(modifier = Modifier.height(10.dp))

        // Size Input
        Text("ORDER SIZE (${uiState.selectedAsset.name})", fontSize = 11.sp, fontWeight = FontWeight.Bold, color = textMutedColor)
        Spacer(modifier = Modifier.height(6.dp))
        OutlinedTextField(
            value = sizeBtc,
            onValueChange = { sizeBtc = it },
            modifier = Modifier.fillMaxWidth().testTag("size_input"),
            colors = OutlinedTextFieldDefaults.colors(
                focusedBorderColor = BrandBlue,
                unfocusedBorderColor = borderColor,
                focusedContainerColor = cardColor,
                unfocusedContainerColor = cardColor,
                focusedTextColor = textColor,
                unfocusedTextColor = textColor
            ),
            shape = RoundedCornerShape(10.dp),
            singleLine = true,
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal)
        )

        Spacer(modifier = Modifier.height(14.dp))

        // TP / SL
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text("TAKE PROFIT", fontSize = 10.sp, fontWeight = FontWeight.Bold, color = SemanticPositive)
                Spacer(modifier = Modifier.height(4.dp))
                OutlinedTextField(
                    value = takeProfit,
                    onValueChange = { takeProfit = it },
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedBorderColor = SemanticPositive,
                        unfocusedBorderColor = borderColor,
                        focusedContainerColor = cardColor,
                        unfocusedContainerColor = cardColor,
                        focusedTextColor = textColor,
                        unfocusedTextColor = textColor
                    ),
                    shape = RoundedCornerShape(8.dp),
                    singleLine = true
                )
            }
            Column(modifier = Modifier.weight(1f)) {
                Text("STOP LOSS", fontSize = 10.sp, fontWeight = FontWeight.Bold, color = SemanticNegative)
                Spacer(modifier = Modifier.height(4.dp))
                OutlinedTextField(
                    value = stopLoss,
                    onValueChange = { stopLoss = it },
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedBorderColor = SemanticNegative,
                        unfocusedBorderColor = borderColor,
                        focusedContainerColor = cardColor,
                        unfocusedContainerColor = cardColor,
                        focusedTextColor = textColor,
                        unfocusedTextColor = textColor
                    ),
                    shape = RoundedCornerShape(8.dp),
                    singleLine = true
                )
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Order Cost Breakdown
        Surface(
            shape = RoundedCornerShape(12.dp),
            color = cardColor,
            border = BorderStroke(1.dp, borderColor),
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(modifier = Modifier.padding(14.dp)) {
                Text("Execution estimate", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = textColor)
                Spacer(modifier = Modifier.height(10.dp))
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text("Notional Value", fontSize = 11.sp, color = textMutedColor)
                    Text("$${String.format("%,.2f", notionalUsd)}", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = textColor)
                }
                Spacer(modifier = Modifier.height(4.dp))
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text("Initial Margin", fontSize = 11.sp, color = textMutedColor)
                    Text("$${String.format("%,.2f", marginRequired)}", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = BrandBlue)
                }
                Spacer(modifier = Modifier.height(4.dp))
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text("Simulated Fee (0.04%)", fontSize = 11.sp, color = textMutedColor)
                    Text("$${String.format("%.2f", estFee)}", fontSize = 12.sp, color = textColor)
                }
                Spacer(modifier = Modifier.height(4.dp))
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text("Est. Slippage (0.02%)", fontSize = 11.sp, color = textMutedColor)
                    Text("$${String.format("%.2f", estSlippage)}", fontSize = 12.sp, color = textColor)
                }
            }
        }

        Spacer(modifier = Modifier.height(20.dp))

        Button(
            onClick = {
                viewModel.placePaperOrder(
                    symbol = "${uiState.selectedAsset.name}/USDT",
                    direction = if (side == "BUY") "LONG" else "SHORT",
                    sizeUsd = notionalUsd,
                    stopLossPct = 1.5,
                    takeProfitPct = 2.0
                )
            },
            colors = ButtonDefaults.buttonColors(
                containerColor = if (side == "BUY") SemanticPositive else SemanticNegative,
                contentColor = Color.White
            ),
            shape = RoundedCornerShape(10.dp),
            modifier = Modifier
                .fillMaxWidth()
                .height(48.dp)
                .testTag("submit_paper_order_button")
        ) {
            Text("SUBMIT PAPER ORDER", fontSize = 13.sp, fontWeight = FontWeight.Bold, letterSpacing = 0.5.sp)
        }

        Spacer(modifier = Modifier.height(60.dp))
    }
}

