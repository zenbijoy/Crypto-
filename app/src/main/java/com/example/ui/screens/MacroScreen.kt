package com.example.ui.screens

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.ui.theme.*
import com.example.ui.viewmodel.CryptoScopeViewModel

@Composable
fun MacroScreen(viewModel: CryptoScopeViewModel) {
    val macro = remember { viewModel.repository.getMacro() }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(BackgroundDark)
            .padding(horizontal = 16.dp)
            .verticalScroll(rememberScrollState())
            .testTag("macro_screen")
    ) {
        Spacer(modifier = Modifier.height(12.dp))

        // Next High-Impact Event Hero Card
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
                    Text("NEXT HIGH-IMPACT EVENT", fontSize = 10.sp, fontWeight = FontWeight.Bold, color = TextMuted)
                    Surface(shape = RoundedCornerShape(4.dp), color = BrandGoldLight) {
                        Text(macro.countdown, fontSize = 10.sp, fontWeight = FontWeight.Bold, color = BrandGold, modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp))
                    }
                }
                Spacer(modifier = Modifier.height(8.dp))
                Text(macro.nextEvent, fontSize = 20.sp, fontWeight = FontWeight.Bold, color = TextPrimary)
                Spacer(modifier = Modifier.height(4.dp))
                Text("Point-in-time observations strictly enforced • Models reduce risk automatically prior to release.", fontSize = 11.sp, color = TextMuted)
            }
        }

        Spacer(modifier = Modifier.height(14.dp))

        // Macro Snapshot 2x3 Grid
        Text("Macro snapshot", fontSize = 13.sp, fontWeight = FontWeight.Bold, color = TextPrimary)
        Spacer(modifier = Modifier.height(8.dp))

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            MacroMetricTile("Fed Funds", macro.fedFundsRate, Modifier.weight(1f))
            MacroMetricTile("US 10Y", macro.us10yYield, Modifier.weight(1f))
        }
        Spacer(modifier = Modifier.height(8.dp))
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            MacroMetricTile("DXY", macro.dxyIndex, Modifier.weight(1f))
            MacroMetricTile("S&P 500", macro.sp500Change, Modifier.weight(1f), isPositive = true)
        }
        Spacer(modifier = Modifier.height(8.dp))
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            MacroMetricTile("Gold", macro.goldPrice, Modifier.weight(1f))
            MacroMetricTile("VIX", macro.vix, Modifier.weight(1f))
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Event Calendar
        Text("Event calendar", fontSize = 13.sp, fontWeight = FontWeight.Bold, color = TextPrimary)
        Spacer(modifier = Modifier.height(8.dp))

        macro.events.forEach { ev ->
            Surface(
                shape = RoundedCornerShape(12.dp),
                color = SurfaceDark,
                border = BorderStroke(1.dp, BorderColor),
                modifier = Modifier.fillMaxWidth().padding(bottom = 8.dp)
            ) {
                Row(
                    modifier = Modifier.padding(14.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text(ev.timeOffset, fontSize = 12.sp, fontWeight = FontWeight.Bold, color = BrandGold, modifier = Modifier.width(36.dp))
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(ev.name, fontSize = 13.sp, fontWeight = FontWeight.SemiBold, color = TextPrimary)
                    }
                    Surface(
                        shape = RoundedCornerShape(4.dp),
                        color = if (ev.impact == "HIGH") SemanticNegativeLight else BrandGoldLight
                    ) {
                        Text(
                            text = ev.impact,
                            fontSize = 9.sp,
                            fontWeight = FontWeight.Bold,
                            color = if (ev.impact == "HIGH") SemanticNegative else BrandGold,
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 2.dp)
                        )
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(60.dp))
    }
}

@Composable
private fun MacroMetricTile(
    label: String,
    value: String,
    modifier: Modifier = Modifier,
    isPositive: Boolean = false
) {
    Surface(
        shape = RoundedCornerShape(10.dp),
        color = SurfaceDark,
        border = BorderStroke(1.dp, BorderColor),
        modifier = modifier
    ) {
        Column(modifier = Modifier.padding(12.dp)) {
            Text(label, fontSize = 10.sp, color = TextMuted)
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                value,
                fontSize = 15.sp,
                fontWeight = FontWeight.Bold,
                color = if (isPositive) SemanticPositive else TextPrimary
            )
        }
    }
}
