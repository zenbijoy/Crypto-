package com.example.ui.screens

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.ui.theme.*
import com.example.ui.viewmodel.CryptoScopeViewModel
import com.example.ui.viewmodel.ScreenRoute

@Composable
fun MoreHubScreen(viewModel: CryptoScopeViewModel) {
    val uiState by viewModel.uiState.collectAsState()
    val isDark = uiState.isDarkTheme
    val bgColor = if (isDark) DarkBackground else LightBackground
    val cardColor = if (isDark) DarkSurface else LightSurface
    val borderColor = if (isDark) DarkBorder else LightBorder
    val textColor = if (isDark) DarkTextPrimary else LightTextPrimary
    val textMutedColor = if (isDark) DarkTextMuted else LightTextMuted

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(bgColor)
            .padding(horizontal = 16.dp)
            .verticalScroll(rememberScrollState())
            .testTag("more_hub_screen")
    ) {
        Spacer(modifier = Modifier.height(12.dp))

        // Profile Strip
        Surface(
            shape = RoundedCornerShape(14.dp),
            color = cardColor,
            border = BorderStroke(1.dp, borderColor),
            modifier = Modifier
                .fillMaxWidth()
                .clickable { viewModel.navigateTo(ScreenRoute.PROFILE) }
                .testTag("profile_hub_card")
        ) {
            Row(
                modifier = Modifier.padding(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Box(
                    modifier = Modifier
                        .size(44.dp)
                        .clip(CircleShape)
                        .background(if (isDark) DarkSurfaceRaised else LightSurfaceRaised)
                        .border(1.5.dp, BrandBlue, CircleShape),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = "JS",
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Bold,
                        color = BrandBlue
                    )
                }
                Spacer(modifier = Modifier.width(12.dp))
                Column(modifier = Modifier.weight(1f)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text(
                            text = uiState.userName,
                            fontSize = 15.sp,
                            fontWeight = FontWeight.Bold,
                            color = textColor
                        )
                        Spacer(modifier = Modifier.width(6.dp))
                        Surface(
                            shape = RoundedCornerShape(4.dp),
                            color = BrandBlueLight
                        ) {
                            Text(
                                text = "PRO QUANT",
                                fontSize = 9.sp,
                                fontWeight = FontWeight.Bold,
                                color = BrandBlue,
                                modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                            )
                        }
                    }
                    Spacer(modifier = Modifier.height(2.dp))
                    Text(
                        text = uiState.userEmail,
                        fontSize = 12.sp,
                        color = textMutedColor
                    )
                }
                Icon(
                    imageVector = Icons.Default.ChevronRight,
                    contentDescription = null,
                    tint = textMutedColor
                )
            }
        }

        Spacer(modifier = Modifier.height(20.dp))

        // Intelligence Modules
        Text(
            text = "INTELLIGENCE MODULES",
            fontSize = 11.sp,
            fontWeight = FontWeight.Bold,
            color = textMutedColor,
            letterSpacing = 0.8.sp
        )
        Spacer(modifier = Modifier.height(8.dp))

        HubRowItem(
            icon = Icons.Default.Analytics,
            title = "Derivatives Analytics",
            subtitle = "Funding rates, open interest, long/short ratio",
            cardColor = cardColor,
            borderColor = borderColor,
            textColor = textColor,
            textMutedColor = textMutedColor,
            isDark = isDark,
            onClick = { viewModel.navigateTo(ScreenRoute.ASSET_DETAIL) }
        )
        Spacer(modifier = Modifier.height(8.dp))

        HubRowItem(
            icon = Icons.Default.AccountBalanceWallet,
            title = "Paper Trading Terminal",
            subtitle = "Simulated execution with realistic slippage & fills",
            badge = "LIVE",
            badgeColor = SemanticPositive,
            cardColor = cardColor,
            borderColor = borderColor,
            textColor = textColor,
            textMutedColor = textMutedColor,
            isDark = isDark,
            onClick = { viewModel.navigateTo(ScreenRoute.PAPER_DASHBOARD) }
        )
        Spacer(modifier = Modifier.height(8.dp))

        HubRowItem(
            icon = Icons.Default.Timeline,
            title = "Prediction Audit History",
            subtitle = "Brier scores, resolved outcomes, calibration log",
            cardColor = cardColor,
            borderColor = borderColor,
            textColor = textColor,
            textMutedColor = textMutedColor,
            isDark = isDark,
            onClick = { viewModel.navigateTo(ScreenRoute.PREDICTION_HISTORY) }
        )
        Spacer(modifier = Modifier.height(8.dp))

        HubRowItem(
            icon = Icons.Default.Assessment,
            title = "Model Registry & Champion / Challenger",
            subtitle = "Ensemble zoo, walk-forward validation & Brier curves",
            cardColor = cardColor,
            borderColor = borderColor,
            textColor = textColor,
            textMutedColor = textMutedColor,
            isDark = isDark,
            onClick = { viewModel.navigateTo(ScreenRoute.MODEL_PERFORMANCE) }
        )

        Spacer(modifier = Modifier.height(20.dp))

        // System & Diagnostics
        Text(
            text = "BACKEND ARCHITECTURE & TELEMETRY",
            fontSize = 11.sp,
            fontWeight = FontWeight.Bold,
            color = textMutedColor,
            letterSpacing = 0.8.sp
        )
        Spacer(modifier = Modifier.height(8.dp))

        HubRowItem(
            icon = Icons.Default.Memory,
            title = "System Health & Pipeline Workers",
            subtitle = "FastAPI, 11 provider adapters, Redis & Data Quality",
            badge = if (uiState.circuitBreakerTriggered) "CIRCUIT OPEN" else "HEALTHY",
            badgeColor = if (uiState.circuitBreakerTriggered) SemanticNegative else SemanticPositive,
            cardColor = cardColor,
            borderColor = borderColor,
            textColor = textColor,
            textMutedColor = textMutedColor,
            isDark = isDark,
            onClick = { viewModel.navigateTo(ScreenRoute.SYSTEM_HEALTH) }
        )
        Spacer(modifier = Modifier.height(8.dp))

        HubRowItem(
            icon = Icons.Default.Star,
            title = "Watchlist & Pinned Assets",
            subtitle = "Favorite markets stored in Room with floating price widget",
            cardColor = cardColor,
            borderColor = borderColor,
            textColor = textColor,
            textMutedColor = textMutedColor,
            isDark = isDark,
            onClick = { viewModel.navigateTo(ScreenRoute.WATCHLIST) }
        )
        Spacer(modifier = Modifier.height(8.dp))

        HubRowItem(
            icon = Icons.Default.NotificationsActive,
            title = "Price Threshold Alerts",
            subtitle = "Set & monitor target prices with Room local database",
            cardColor = cardColor,
            borderColor = borderColor,
            textColor = textColor,
            textMutedColor = textMutedColor,
            isDark = isDark,
            onClick = { viewModel.navigateTo(ScreenRoute.PRICE_THRESHOLDS) }
        )
        Spacer(modifier = Modifier.height(8.dp))

        HubRowItem(
            icon = Icons.Default.Notifications,
            title = "Notifications & Live Signal Feed",
            subtitle = "Configured webhooks, execution logs, alerts",
            cardColor = cardColor,
            borderColor = borderColor,
            textColor = textColor,
            textMutedColor = textMutedColor,
            isDark = isDark,
            onClick = { viewModel.navigateTo(ScreenRoute.NOTIFICATIONS) }
        )
        Spacer(modifier = Modifier.height(8.dp))

        HubRowItem(
            icon = Icons.Default.Search,
            title = "Global Market & Signal Search",
            subtitle = "Find symbols, indicator setups, alert rules",
            cardColor = cardColor,
            borderColor = borderColor,
            textColor = textColor,
            textMutedColor = textMutedColor,
            isDark = isDark,
            onClick = { viewModel.navigateTo(ScreenRoute.GLOBAL_SEARCH) }
        )

        Spacer(modifier = Modifier.height(20.dp))

        // Configuration & Risk
        Text(
            text = "SETTINGS & GOVERNANCE",
            fontSize = 11.sp,
            fontWeight = FontWeight.Bold,
            color = textMutedColor,
            letterSpacing = 0.8.sp
        )
        Spacer(modifier = Modifier.height(8.dp))

        HubRowItem(
            icon = Icons.Default.Settings,
            title = "Preferences & App Settings",
            subtitle = "Chart style, currency, notification threshold",
            cardColor = cardColor,
            borderColor = borderColor,
            textColor = textColor,
            textMutedColor = textMutedColor,
            isDark = isDark,
            onClick = { viewModel.navigateTo(ScreenRoute.SETTINGS) }
        )
        Spacer(modifier = Modifier.height(8.dp))

        HubRowItem(
            icon = Icons.Default.Security,
            title = "Security & Biometrics",
            subtitle = "API key encryption, session timeout, pin lock",
            cardColor = cardColor,
            borderColor = borderColor,
            textColor = textColor,
            textMutedColor = textMutedColor,
            isDark = isDark,
            onClick = { viewModel.navigateTo(ScreenRoute.SECURITY) }
        )
        Spacer(modifier = Modifier.height(8.dp))

        HubRowItem(
            icon = Icons.Default.Shield,
            title = "Risk Disclosure & Methodology",
            subtitle = "Probabilistic modeling limits & paper disclaimers",
            cardColor = cardColor,
            borderColor = borderColor,
            textColor = textColor,
            textMutedColor = textMutedColor,
            isDark = isDark,
            onClick = { viewModel.navigateTo(ScreenRoute.ABOUT_RISK) }
        )

        Spacer(modifier = Modifier.height(24.dp))

        // Sign Out Button
        OutlinedButton(
            onClick = { viewModel.signOut() },
            colors = ButtonDefaults.outlinedButtonColors(
                containerColor = cardColor,
                contentColor = SemanticNegative
            ),
            border = BorderStroke(1.dp, SemanticNegative.copy(alpha = 0.3f)),
            shape = RoundedCornerShape(10.dp),
            modifier = Modifier
                .fillMaxWidth()
                .height(44.dp)
                .testTag("sign_out_button")
        ) {
            Icon(
                imageVector = Icons.Default.ExitToApp,
                contentDescription = null,
                tint = SemanticNegative,
                modifier = Modifier.size(16.dp)
            )
            Spacer(modifier = Modifier.width(8.dp))
            Text("Sign Out of Workspace", fontSize = 13.sp, fontWeight = FontWeight.SemiBold)
        }

        Spacer(modifier = Modifier.height(80.dp))
    }
}

@Composable
fun HubRowItem(
    icon: ImageVector,
    title: String,
    subtitle: String,
    badge: String? = null,
    badgeColor: Color = BrandBlue,
    cardColor: Color = DarkSurface,
    borderColor: Color = DarkBorder,
    textColor: Color = DarkTextPrimary,
    textMutedColor: Color = DarkTextMuted,
    isDark: Boolean = true,
    onClick: () -> Unit
) {
    Surface(
        shape = RoundedCornerShape(12.dp),
        color = cardColor,
        border = BorderStroke(1.dp, borderColor),
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick)
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 14.dp, vertical = 12.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(36.dp)
                    .clip(RoundedCornerShape(8.dp))
                    .background(if (isDark) DarkSurfaceRaised else LightSurfaceRaised),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = null,
                    tint = BrandBlue,
                    modifier = Modifier.size(18.dp)
                )
            }
            Spacer(modifier = Modifier.width(12.dp))
            Column(modifier = Modifier.weight(1f)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(
                        text = title,
                        fontSize = 13.sp,
                        fontWeight = FontWeight.SemiBold,
                        color = textColor
                    )
                    if (badge != null) {
                        Spacer(modifier = Modifier.width(6.dp))
                        Surface(
                            shape = RoundedCornerShape(4.dp),
                            color = badgeColor.copy(alpha = 0.15f)
                        ) {
                            Text(
                                text = badge,
                                fontSize = 9.sp,
                                fontWeight = FontWeight.Bold,
                                color = badgeColor,
                                modifier = Modifier.padding(horizontal = 5.dp, vertical = 1.dp)
                            )
                        }
                    }
                }
                Spacer(modifier = Modifier.height(2.dp))
                Text(
                    text = subtitle,
                    fontSize = 11.sp,
                    color = textMutedColor,
                    lineHeight = 14.sp
                )
            }
            Icon(
                imageVector = Icons.Default.ChevronRight,
                contentDescription = null,
                tint = textMutedColor,
                modifier = Modifier.size(18.dp)
            )
        }
    }
}

