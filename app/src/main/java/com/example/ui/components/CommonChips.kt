package com.example.ui.components

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.core.model.*
import com.example.ui.theme.*

@Composable
fun DataQualityChip(
    score: Int,
    modifier: Modifier = Modifier,
    isDegraded: Boolean = false
) {
    val bgColor = if (isDegraded) NegativeSurface else SurfaceRaised
    val textColor = if (isDegraded) SemanticNegative else if (score >= 90) SemanticPositive else BrandGold
    val borderCol = if (isDegraded) SemanticNegative.copy(alpha = 0.5f) else BorderColor

    Surface(
        shape = RoundedCornerShape(20.dp),
        color = bgColor,
        border = BorderStroke(1.dp, borderCol),
        modifier = modifier.testTag("data_quality_chip")
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            modifier = Modifier.padding(horizontal = 8.dp, vertical = 3.dp)
        ) {
            Box(
                modifier = Modifier
                    .size(6.dp)
                    .clip(CircleShape)
                    .background(textColor)
            )
            Spacer(modifier = Modifier.width(4.dp))
            Text(
                text = "QUALITY $score/100",
                fontSize = 10.sp,
                fontWeight = FontWeight.SemiBold,
                color = textColor,
                letterSpacing = 0.3.sp
            )
        }
    }
}

@Composable
fun RegimeChip(
    regimeText: String,
    modifier: Modifier = Modifier
) {
    Surface(
        shape = RoundedCornerShape(20.dp),
        color = InfoSurface,
        border = BorderStroke(1.dp, SemanticInfo.copy(alpha = 0.4f)),
        modifier = modifier.testTag("regime_chip")
    ) {
        Text(
            text = regimeText.uppercase(),
            fontSize = 10.sp,
            fontWeight = FontWeight.Bold,
            color = SemanticInfo,
            modifier = Modifier.padding(horizontal = 8.dp, vertical = 3.dp),
            letterSpacing = 0.4.sp
        )
    }
}

@Composable
fun SignalBadge(
    signal: SignalType,
    modifier: Modifier = Modifier
) {
    val bgCol: Color
    val txtCol: Color
    when (signal) {
        SignalType.STRONG_LONG, SignalType.LONG -> {
            bgCol = PositiveSurface
            txtCol = SemanticPositive
        }
        SignalType.STRONG_SHORT, SignalType.SHORT -> {
            bgCol = NegativeSurface
            txtCol = SemanticNegative
        }
        SignalType.NEUTRAL -> {
            bgCol = SurfaceRaised
            txtCol = TextMuted
        }
        SignalType.ABSTAINED -> {
            bgCol = WarningSurface
            txtCol = SemanticWarning
        }
    }

    Surface(
        shape = RoundedCornerShape(6.dp),
        color = bgCol,
        border = BorderStroke(1.dp, txtCol.copy(alpha = 0.4f)),
        modifier = modifier.testTag("signal_badge")
    ) {
        Text(
            text = signal.title,
            fontSize = 12.sp,
            fontWeight = FontWeight.Bold,
            color = txtCol,
            modifier = Modifier.padding(horizontal = 10.dp, vertical = 4.dp),
            letterSpacing = 0.5.sp
        )
    }
}

@Composable
fun RiskBadge(
    risk: RiskLevel,
    modifier: Modifier = Modifier
) {
    val bgCol: Color
    val txtCol: Color
    when (risk) {
        RiskLevel.LOW -> {
            bgCol = SemanticPositiveLight
            txtCol = SemanticPositive
        }
        RiskLevel.MEDIUM -> {
            bgCol = BrandGoldLight
            txtCol = BrandGold
        }
        RiskLevel.HIGH, RiskLevel.CRITICAL -> {
            bgCol = SemanticNegativeLight
            txtCol = SemanticNegative
        }
    }

    Surface(
        shape = RoundedCornerShape(4.dp),
        color = bgCol,
        modifier = modifier.testTag("risk_badge")
    ) {
        Text(
            text = "RISK: ${risk.name}",
            fontSize = 9.sp,
            fontWeight = FontWeight.Bold,
            color = txtCol,
            modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
        )
    }
}

@Composable
fun NoTradeExplanationCard(
    reason: String,
    modifier: Modifier = Modifier
) {
    Surface(
        shape = RoundedCornerShape(12.dp),
        color = DarkSurface,
        border = BorderStroke(1.dp, DarkBorder),
        modifier = modifier.fillMaxWidth()
    ) {
        Column(modifier = Modifier.padding(14.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    imageVector = Icons.Default.Shield,
                    contentDescription = null,
                    tint = BrandGold,
                    modifier = Modifier.size(18.dp)
                )
                Spacer(modifier = Modifier.width(6.dp))
                Text(
                    text = "NO-TRADE ACTIVE (CAPITAL PRESERVATION)",
                    fontSize = 12.sp,
                    fontWeight = FontWeight.Bold,
                    color = BrandGold
                )
            }
            Spacer(modifier = Modifier.height(6.dp))
            Text(
                text = reason,
                fontSize = 12.sp,
                color = DarkTextPrimary,
                lineHeight = 16.sp
            )
            Spacer(modifier = Modifier.height(6.dp))
            Text(
                text = "NO-TRADE is considered a successful state when statistical edge does not exceed costs.",
                fontSize = 10.sp,
                color = DarkTextMuted
            )
        }
    }
}

@Composable
fun SimulationWatermarkBadge(
    modifier: Modifier = Modifier
) {
    Surface(
        shape = RoundedCornerShape(6.dp),
        color = BrandGoldLight,
        border = BorderStroke(1.dp, BrandGold.copy(alpha = 0.5f)),
        modifier = modifier.testTag("paper_simulation_badge")
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            modifier = Modifier.padding(horizontal = 8.dp, vertical = 3.dp)
        ) {
            Icon(
                imageVector = Icons.Default.AccountBalanceWallet,
                contentDescription = null,
                tint = BrandGold,
                modifier = Modifier.size(12.dp)
            )
            Spacer(modifier = Modifier.width(4.dp))
            Text(
                text = "NO REAL FUNDS / PAPER SIMULATION",
                fontSize = 9.sp,
                fontWeight = FontWeight.Bold,
                color = BrandGold,
                letterSpacing = 0.4.sp
            )
        }
    }
}
