package com.example.ui.screens

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.ui.theme.*
import com.example.ui.viewmodel.CryptoScopeViewModel

@Composable
fun PredictionInspectorScreen(viewModel: CryptoScopeViewModel) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(BackgroundDark)
            .padding(horizontal = 16.dp)
            .verticalScroll(rememberScrollState())
            .testTag("prediction_inspector_screen")
    ) {
        Spacer(modifier = Modifier.height(12.dp))

        // Top App Bar
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            IconButton(onClick = { viewModel.navigateBack() }, modifier = Modifier.size(32.dp)) {
                Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back", tint = TextPrimary)
            }
            Spacer(modifier = Modifier.width(6.dp))
            Column {
                Text("Prediction Audit Detail", fontSize = 18.sp, fontWeight = FontWeight.Bold, color = TextPrimary)
                Text("BTC/USDT • 1H Horizon • Resolved", fontSize = 10.sp, color = TextMuted)
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Hero Outcome Card
        Surface(
            shape = RoundedCornerShape(14.dp),
            color = SurfaceDark,
            border = BorderStroke(1.dp, BorderColor),
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Default.CheckCircle, contentDescription = null, tint = SemanticPositive, modifier = Modifier.size(18.dp))
                        Spacer(modifier = Modifier.width(6.dp))
                        Text("RESOLVED IN RANGE", fontSize = 13.sp, fontWeight = FontWeight.Bold, color = SemanticPositive)
                    }
                    Text("Brier: 0.12", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = BrandGold)
                }

                Spacer(modifier = Modifier.height(12.dp))

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Column {
                        Text("Predicted P10-P90", fontSize = 11.sp, color = TextMuted)
                        Text("$108,900 - $110,200", fontSize = 14.sp, fontWeight = FontWeight.Bold, color = TextPrimary)
                    }
                    Column(horizontalAlignment = Alignment.End) {
                        Text("Realized Price", fontSize = 11.sp, color = TextMuted)
                        Text("$109,720.00", fontSize = 14.sp, fontWeight = FontWeight.Bold, color = SemanticPositive)
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Feature Attribution Card
        Surface(
            shape = RoundedCornerShape(14.dp),
            color = SurfaceDark,
            border = BorderStroke(1.dp, BorderColor),
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = "FEATURE ATTRIBUTION (SHAP)",
                    fontSize = 11.sp,
                    fontWeight = FontWeight.Bold,
                    color = TextMuted,
                    letterSpacing = 0.8.sp
                )
                Spacer(modifier = Modifier.height(12.dp))

                FeatureShapRow("Order Book Depth Delta (50 Levels)", "+38%", true)
                FeatureShapRow("Funding Rate Deviation (Perp-Spot)", "+24%", true)
                FeatureShapRow("Taker Buy Volume Acceleration", "+18%", true)
                FeatureShapRow("Liquidation Cascade Cluster", "-9%", false)
                FeatureShapRow("On-Chain Exchange Outflow", "+12%", true)
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Risk Engine Gate
        Surface(
            shape = RoundedCornerShape(14.dp),
            color = SurfaceDark,
            border = BorderStroke(1.dp, BorderColor),
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = "RISK ENGINE AUDIT",
                    fontSize = 11.sp,
                    fontWeight = FontWeight.Bold,
                    color = TextMuted,
                    letterSpacing = 0.8.sp
                )
                Spacer(modifier = Modifier.height(10.dp))

                Text("• Minimum Confidence: 84% (Threshold: 70%) → PASS", fontSize = 12.sp, color = TextPrimary)
                Spacer(modifier = Modifier.height(4.dp))
                Text("• Sub-Model Agreement: 4/4 models bullish → PASS", fontSize = 12.sp, color = TextPrimary)
                Spacer(modifier = Modifier.height(4.dp))
                Text("• Spread Slippage Check: 0.012% → PASS", fontSize = 12.sp, color = TextPrimary)
                Spacer(modifier = Modifier.height(4.dp))
                Text("• Circuit Breaker Gate: Clean → PASS", fontSize = 12.sp, color = TextPrimary)
            }
        }

        Spacer(modifier = Modifier.height(30.dp))
    }
}

@Composable
private fun FeatureShapRow(name: String, weight: String, positive: Boolean) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 5.dp),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(name, fontSize = 12.sp, color = TextPrimary)
        Text(
            weight,
            fontSize = 12.sp,
            fontWeight = FontWeight.Bold,
            color = if (positive) SemanticPositive else SemanticNegative
        )
    }
}
