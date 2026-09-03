package com.example.ui.screens

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
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
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.ui.theme.*
import com.example.ui.viewmodel.CryptoScopeViewModel

@Composable
fun CreateAlertScreen(viewModel: CryptoScopeViewModel) {
    val uiState by viewModel.uiState.collectAsState()
    val isDark = uiState.isDarkTheme
    val bgColor = if (isDark) DarkBackground else LightBackground
    val cardColor = if (isDark) DarkSurface else LightSurface
    val borderColor = if (isDark) DarkBorder else LightBorder
    val textColor = if (isDark) DarkTextPrimary else LightTextPrimary
    val textMutedColor = if (isDark) DarkTextMuted else LightTextMuted

    var selectedAsset by remember { mutableStateOf("BTC/USDT") }
    var selectedHorizon by remember { mutableStateOf("1 hour") }
    var selectedSignal by remember { mutableStateOf("LONG") }
    var minConfidence by remember { mutableFloatStateOf(80f) }
    var minAgreement by remember { mutableFloatStateOf(75f) }
    var minQuality by remember { mutableFloatStateOf(95f) }
    var cooldownMinutes by remember { mutableStateOf("60 minutes") }
    var requireExpectedEdge by remember { mutableStateOf(true) }
    var requireRiskEngineAllow by remember { mutableStateOf(true) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(bgColor)
            .padding(horizontal = 16.dp)
            .verticalScroll(rememberScrollState())
            .testTag("create_alert_screen")
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
                Text("Create Alert", fontSize = 18.sp, fontWeight = FontWeight.Bold, color = textColor)
                Text("Rule Builder", fontSize = 10.sp, color = textMutedColor)
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Form Fields
        AlertFormTile("Asset", selectedAsset, cardColor, borderColor, textColor, textMutedColor) {
            selectedAsset = if (selectedAsset == "BTC/USDT") "ETH/USDT" else if (selectedAsset == "ETH/USDT") "SOL/USDT" else "BTC/USDT"
        }
        Spacer(modifier = Modifier.height(8.dp))
        AlertFormTile("Horizon", selectedHorizon, cardColor, borderColor, textColor, textMutedColor) {
            selectedHorizon = if (selectedHorizon == "1 hour") "15m" else if (selectedHorizon == "15m") "4h" else "1 hour"
        }
        Spacer(modifier = Modifier.height(8.dp))
        AlertFormTile("Signal", selectedSignal, cardColor, borderColor, textColor, textMutedColor) {
            selectedSignal = if (selectedSignal == "LONG") "SHORT" else if (selectedSignal == "SHORT") "BREAKOUT" else "LONG"
        }

        Spacer(modifier = Modifier.height(14.dp))

        // Sliders
        Text("MIN CONFIDENCE: ${minConfidence.toInt()} / 100", fontSize = 11.sp, fontWeight = FontWeight.Bold, color = textMutedColor)
        Slider(
            value = minConfidence,
            onValueChange = { minConfidence = it },
            valueRange = 50f..100f,
            colors = SliderDefaults.colors(thumbColor = BrandBlue, activeTrackColor = BrandBlue)
        )

        Text("MIN AGREEMENT: ${minAgreement.toInt()}%", fontSize = 11.sp, fontWeight = FontWeight.Bold, color = textMutedColor)
        Slider(
            value = minAgreement,
            onValueChange = { minAgreement = it },
            valueRange = 50f..100f,
            colors = SliderDefaults.colors(thumbColor = BrandPurpleAI, activeTrackColor = BrandPurpleAI)
        )

        Text("MIN DATA QUALITY: ${minQuality.toInt()} / 100", fontSize = 11.sp, fontWeight = FontWeight.Bold, color = textMutedColor)
        Slider(
            value = minQuality,
            onValueChange = { minQuality = it },
            valueRange = 70f..100f,
            colors = SliderDefaults.colors(thumbColor = SemanticPositive, activeTrackColor = SemanticPositive)
        )

        Spacer(modifier = Modifier.height(6.dp))
        AlertFormTile("Cooldown", cooldownMinutes, cardColor, borderColor, textColor, textMutedColor) {
            cooldownMinutes = if (cooldownMinutes == "60 minutes") "30 minutes" else if (cooldownMinutes == "30 minutes") "15 minutes" else "60 minutes"
        }

        Spacer(modifier = Modifier.height(14.dp))

        // Switches
        Surface(
            shape = RoundedCornerShape(10.dp),
            color = cardColor,
            border = BorderStroke(1.dp, borderColor),
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(modifier = Modifier.padding(12.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text("Require expected edge > costs", fontSize = 12.sp, color = textColor)
                    Switch(
                        checked = requireExpectedEdge,
                        onCheckedChange = { requireExpectedEdge = it }
                    )
                }
                HorizontalDivider(color = borderColor, modifier = Modifier.padding(vertical = 6.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text("Require risk engine ALLOW", fontSize = 12.sp, color = textColor)
                    Switch(
                        checked = requireRiskEngineAllow,
                        onCheckedChange = { requireRiskEngineAllow = it }
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(20.dp))

        Button(
            onClick = {
                viewModel.createAlertRule(
                    asset = selectedAsset.take(3),
                    horizon = selectedHorizon,
                    signal = selectedSignal,
                    minConfidence = minConfidence.toInt(),
                    minAgreement = minAgreement.toInt(),
                    minQuality = minQuality.toInt(),
                    cooldown = if (cooldownMinutes.contains("30")) 30 else (if (cooldownMinutes.contains("15")) 15 else 60)
                )
            },
            colors = ButtonDefaults.buttonColors(containerColor = BrandBlue, contentColor = Color.White),
            shape = RoundedCornerShape(10.dp),
            modifier = Modifier
                .fillMaxWidth()
                .height(48.dp)
                .testTag("save_alert_button")
        ) {
            Text("SAVE ALERT", fontSize = 13.sp, fontWeight = FontWeight.Bold, letterSpacing = 0.5.sp)
        }

        Spacer(modifier = Modifier.height(60.dp))
    }
}

@Composable
private fun AlertFormTile(
    label: String,
    value: String,
    cardColor: Color,
    borderColor: Color,
    textColor: Color,
    textMutedColor: Color,
    onClick: () -> Unit
) {
    Surface(
        shape = RoundedCornerShape(10.dp),
        color = cardColor,
        border = BorderStroke(1.dp, borderColor),
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick)
    ) {
        Row(
            modifier = Modifier.padding(14.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(label, fontSize = 11.sp, color = textMutedColor)
            Text(value, fontSize = 13.sp, fontWeight = FontWeight.Bold, color = textColor)
        }
    }
}

