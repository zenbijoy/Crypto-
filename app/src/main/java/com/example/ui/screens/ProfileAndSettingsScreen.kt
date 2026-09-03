package com.example.ui.screens

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
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
import com.example.ui.theme.*
import com.example.ui.viewmodel.CryptoScopeViewModel

@Composable
fun ProfileScreen(viewModel: CryptoScopeViewModel) {
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
            .testTag("profile_screen")
    ) {
        Spacer(modifier = Modifier.height(12.dp))

        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            IconButton(onClick = { viewModel.navigateBack() }, modifier = Modifier.size(32.dp)) {
                Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back", tint = textColor)
            }
            Spacer(modifier = Modifier.width(6.dp))
            Column {
                Text("Trader Profile", fontSize = 18.sp, fontWeight = FontWeight.Bold, color = textColor)
                Text("Workspace Identity & Pro Subscription", fontSize = 10.sp, color = textMutedColor)
            }
        }

        Spacer(modifier = Modifier.height(20.dp))

        // Hero Profile Card
        Surface(
            shape = RoundedCornerShape(16.dp),
            color = cardColor,
            border = BorderStroke(1.dp, borderColor),
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(
                modifier = Modifier.padding(20.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Box(
                    modifier = Modifier
                        .size(64.dp)
                        .clip(CircleShape)
                        .background(if (isDark) DarkSurfaceRaised else LightSurfaceRaised)
                        .border(2.dp, BrandGold, CircleShape),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = "JS",
                        fontSize = 24.sp,
                        fontWeight = FontWeight.Bold,
                        color = BrandGold
                    )
                }

                Spacer(modifier = Modifier.height(12.dp))

                Text(
                    text = uiState.userName,
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold,
                    color = textColor
                )

                Text(
                    text = uiState.userEmail,
                    fontSize = 12.sp,
                    color = textMutedColor
                )

                Spacer(modifier = Modifier.height(8.dp))

                Surface(
                    shape = RoundedCornerShape(20.dp),
                    color = BrandGold.copy(alpha = 0.15f)
                ) {
                    Text(
                        text = "PRO QUANT SUBSCRIBER",
                        fontSize = 10.sp,
                        fontWeight = FontWeight.Bold,
                        color = BrandGold,
                        modifier = Modifier.padding(horizontal = 10.dp, vertical = 4.dp)
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Paper Balance Reset
        Surface(
            shape = RoundedCornerShape(14.dp),
            color = cardColor,
            border = BorderStroke(1.dp, borderColor),
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("SIMULATION SETTINGS", fontSize = 11.sp, fontWeight = FontWeight.Bold, color = textMutedColor)
                Spacer(modifier = Modifier.height(8.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text("Paper Wallet Balance", fontSize = 13.sp, fontWeight = FontWeight.SemiBold, color = textColor)
                        Text("$10,842.60 USDT", fontSize = 11.sp, color = SemanticPositive)
                    }
                    TextButton(onClick = { /* Reset */ }) {
                        Text("Reset to $10,000", fontSize = 12.sp, color = BrandGold)
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(30.dp))
    }
}

@Composable
fun SettingsScreen(viewModel: CryptoScopeViewModel) {
    val uiState by viewModel.uiState.collectAsState()
    val isDark = uiState.isDarkTheme
    val bgColor = if (isDark) DarkBackground else LightBackground
    val cardColor = if (isDark) DarkSurface else LightSurface
    val borderColor = if (isDark) DarkBorder else LightBorder
    val textColor = if (isDark) DarkTextPrimary else LightTextPrimary
    val textMutedColor = if (isDark) DarkTextMuted else LightTextMuted

    var notificationsEnabled by remember { mutableStateOf(true) }
    var soundEnabled by remember { mutableStateOf(true) }
    var highPrecisionCharts by remember { mutableStateOf(true) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(bgColor)
            .padding(horizontal = 16.dp)
            .verticalScroll(rememberScrollState())
            .testTag("settings_screen")
    ) {
        Spacer(modifier = Modifier.height(12.dp))

        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            IconButton(onClick = { viewModel.navigateBack() }, modifier = Modifier.size(32.dp)) {
                Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back", tint = textColor)
            }
            Spacer(modifier = Modifier.width(6.dp))
            Column {
                Text("App Preferences", fontSize = 18.sp, fontWeight = FontWeight.Bold, color = textColor)
                Text("Theme, Alerts & Display Engine", fontSize = 10.sp, color = textMutedColor)
            }
        }

        Spacer(modifier = Modifier.height(20.dp))

        Surface(
            shape = RoundedCornerShape(14.dp),
            color = cardColor,
            border = BorderStroke(1.dp, borderColor),
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("GENERAL PREFERENCES", fontSize = 11.sp, fontWeight = FontWeight.Bold, color = textMutedColor)
                Spacer(modifier = Modifier.height(12.dp))

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text("Dark Mode", fontSize = 13.sp, fontWeight = FontWeight.SemiBold, color = textColor)
                        Text("Toggle high-contrast dark theme", fontSize = 11.sp, color = textMutedColor)
                    }
                    Switch(
                        checked = uiState.isDarkTheme,
                        onCheckedChange = { viewModel.toggleDarkTheme() }
                    )
                }

                Spacer(modifier = Modifier.height(12.dp))

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text("Signal Notifications", fontSize = 13.sp, fontWeight = FontWeight.SemiBold, color = textColor)
                        Text("Push high-confidence gated signals", fontSize = 11.sp, color = textMutedColor)
                    }
                    Switch(checked = notificationsEnabled, onCheckedChange = { notificationsEnabled = it })
                }

                Spacer(modifier = Modifier.height(12.dp))

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text("Audio Alert Chimes", fontSize = 13.sp, fontWeight = FontWeight.SemiBold, color = textColor)
                        Text("Audio feedback on fills & breaches", fontSize = 11.sp, color = textMutedColor)
                    }
                    Switch(checked = soundEnabled, onCheckedChange = { soundEnabled = it })
                }

                Spacer(modifier = Modifier.height(12.dp))

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text("60 FPS Canvas Rendering", fontSize = 13.sp, fontWeight = FontWeight.SemiBold, color = textColor)
                        Text("Smooth orderbook depth interpolation", fontSize = 11.sp, color = textMutedColor)
                    }
                    Switch(checked = highPrecisionCharts, onCheckedChange = { highPrecisionCharts = it })
                }
            }
        }

        Spacer(modifier = Modifier.height(30.dp))
    }
}

@Composable
fun SecurityScreen(viewModel: CryptoScopeViewModel) {
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
            .testTag("security_screen")
    ) {
        Spacer(modifier = Modifier.height(12.dp))

        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            IconButton(onClick = { viewModel.navigateBack() }, modifier = Modifier.size(32.dp)) {
                Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back", tint = textColor)
            }
            Spacer(modifier = Modifier.width(6.dp))
            Column {
                Text("Security & Encryption", fontSize = 18.sp, fontWeight = FontWeight.Bold, color = textColor)
                Text("Keys, Biometrics & Hardware Protection", fontSize = 10.sp, color = textMutedColor)
            }
        }

        Spacer(modifier = Modifier.height(20.dp))

        Surface(
            shape = RoundedCornerShape(14.dp),
            color = cardColor,
            border = BorderStroke(1.dp, borderColor),
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("ENCRYPTION & VAULT", fontSize = 11.sp, fontWeight = FontWeight.Bold, color = textMutedColor)
                Spacer(modifier = Modifier.height(10.dp))

                Text("• Android Keystore Hardware-backed Master Key: ACTIVE", fontSize = 12.sp, color = SemanticPositive)
                Spacer(modifier = Modifier.height(4.dp))
                Text("• Local Room Database SQLiteCipher: AES-256-GCM", fontSize = 12.sp, color = textColor)
                Spacer(modifier = Modifier.height(4.dp))
                Text("• Zero-Retention Policy on Exchange Secret Keys", fontSize = 12.sp, color = textColor)
            }
        }

        Spacer(modifier = Modifier.height(30.dp))
    }
}

@Composable
fun AboutRiskScreen(viewModel: CryptoScopeViewModel) {
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
            .testTag("about_risk_screen")
    ) {
        Spacer(modifier = Modifier.height(12.dp))

        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            IconButton(onClick = { viewModel.navigateBack() }, modifier = Modifier.size(32.dp)) {
                Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back", tint = textColor)
            }
            Spacer(modifier = Modifier.width(6.dp))
            Column {
                Text("Risk & Methodology", fontSize = 18.sp, fontWeight = FontWeight.Bold, color = textColor)
                Text("Probabilistic Limits & Regulatory Disclosures", fontSize = 10.sp, color = textMutedColor)
            }
        }

        Spacer(modifier = Modifier.height(20.dp))

        Surface(
            shape = RoundedCornerShape(14.dp),
            color = cardColor,
            border = BorderStroke(1.dp, borderColor),
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("DISCLAIMER & METHODOLOGY", fontSize = 11.sp, fontWeight = FontWeight.Bold, color = textMutedColor)
                Spacer(modifier = Modifier.height(10.dp))

                Text(
                    text = "CryptoScope AI is an advanced statistical and machine learning analytics platform for cryptocurrency derivatives markets. All forecasts are probabilistic estimates subject to regime changes, exchange outages, and extreme volatility. CryptoScope is not a broker, does not provide financial or investment advice, and paper trading simulations carry no actual financial liability.",
                    fontSize = 12.sp,
                    color = textMutedColor,
                    lineHeight = 18.sp
                )
            }
        }

        Spacer(modifier = Modifier.height(30.dp))
    }
}

