package com.example.ui.screens

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Pause
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.ui.theme.*
import com.example.ui.viewmodel.CryptoScopeViewModel

@Composable
fun AlertDetailScreen(viewModel: CryptoScopeViewModel) {
    val uiState by viewModel.uiState.collectAsState()
    val isDark = uiState.isDarkTheme
    val bgColor = if (isDark) DarkBackground else LightBackground
    val cardColor = if (isDark) DarkSurface else LightSurface
    val borderColor = if (isDark) DarkBorder else LightBorder
    val textColor = if (isDark) DarkTextPrimary else LightTextPrimary
    val textMutedColor = if (isDark) DarkTextMuted else LightTextMuted

    val triggerHistory = listOf(
        Triple("Today 14:12", "LONG", "Conf 84"),
        Triple("Aug 30 08:15", "LONG", "Conf 81"),
        Triple("Aug 28 10:42", "LONG", "Conf 83")
    )

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(bgColor)
            .padding(horizontal = 16.dp)
            .verticalScroll(rememberScrollState())
            .testTag("alert_detail_screen")
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
                Text("Alert Detail", fontSize = 18.sp, fontWeight = FontWeight.Bold, color = textColor)
                Text("BTC LONG • 1H", fontSize = 10.sp, color = textMutedColor)
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Status Badge & Gate Health Card
        Surface(
            shape = RoundedCornerShape(14.dp),
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
                    Text("RULE HEALTH", fontSize = 10.sp, fontWeight = FontWeight.Bold, color = textMutedColor)
                    Surface(shape = RoundedCornerShape(4.dp), color = SemanticPositiveLight) {
                        Text("ACTIVE", fontSize = 9.sp, fontWeight = FontWeight.Bold, color = SemanticPositive, modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp))
                    }
                }
                Spacer(modifier = Modifier.height(8.dp))
                Text("All gates passing", fontSize = 16.sp, fontWeight = FontWeight.Bold, color = SemanticPositive)
                Spacer(modifier = Modifier.height(10.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text("Confidence 82 ≥ 80", fontSize = 11.sp, color = textMutedColor)
                    Text("Agreement 84 ≥ 75", fontSize = 11.sp, color = textMutedColor)
                }
                Spacer(modifier = Modifier.height(4.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text("Data quality 98 ≥ 95", fontSize = 11.sp, color = textMutedColor)
                    Text("Risk engine ALLOW", fontSize = 11.sp, color = SemanticPositive)
                }
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Trigger History
        Text("Trigger history", fontSize = 13.sp, fontWeight = FontWeight.Bold, color = textColor)
        Spacer(modifier = Modifier.height(8.dp))

        triggerHistory.forEach { (time, sig, conf) ->
            Surface(
                shape = RoundedCornerShape(10.dp),
                color = cardColor,
                border = BorderStroke(1.dp, borderColor),
                modifier = Modifier.fillMaxWidth().padding(bottom = 6.dp)
            ) {
                Row(
                    modifier = Modifier.padding(12.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(time, fontSize = 11.sp, color = textMutedColor)
                    Surface(shape = RoundedCornerShape(4.dp), color = SemanticPositiveLight) {
                        Text(sig, fontSize = 9.sp, fontWeight = FontWeight.Bold, color = SemanticPositive, modifier = Modifier.padding(horizontal = 8.dp, vertical = 2.dp))
                    }
                    Text(conf, fontSize = 11.sp, fontWeight = FontWeight.Bold, color = textColor)
                }
            }
        }

        Spacer(modifier = Modifier.height(24.dp))

        // Action buttons
        Button(
            onClick = { viewModel.pauseAlert(uiState.activeAlertDetailId) },
            colors = ButtonDefaults.buttonColors(
                containerColor = if (isDark) DarkSurfaceRaised else LightSurfaceRaised,
                contentColor = textColor
            ),
            border = BorderStroke(1.dp, borderColor),
            shape = RoundedCornerShape(10.dp),
            modifier = Modifier.fillMaxWidth().height(46.dp)
        ) {
            Icon(Icons.Default.Pause, contentDescription = null, tint = BrandGold, modifier = Modifier.size(16.dp))
            Spacer(modifier = Modifier.width(6.dp))
            Text("PAUSE ALERT", fontSize = 12.sp, fontWeight = FontWeight.Bold)
        }

        Spacer(modifier = Modifier.height(10.dp))

        OutlinedButton(
            onClick = { viewModel.deleteAlert(uiState.activeAlertDetailId) },
            colors = ButtonDefaults.outlinedButtonColors(contentColor = SemanticNegative),
            border = BorderStroke(1.dp, SemanticNegative.copy(alpha = 0.5f)),
            shape = RoundedCornerShape(10.dp),
            modifier = Modifier.fillMaxWidth().height(46.dp)
        ) {
            Icon(Icons.Default.Delete, contentDescription = null, tint = SemanticNegative, modifier = Modifier.size(16.dp))
            Spacer(modifier = Modifier.width(6.dp))
            Text("DELETE ALERT", fontSize = 12.sp, fontWeight = FontWeight.Bold)
        }
    }
}

