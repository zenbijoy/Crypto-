package com.example

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.BackHandler
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.animation.Crossfade
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
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.ui.screens.*
import com.example.ui.theme.*
import com.example.ui.viewmodel.CryptoScopeViewModel
import com.example.ui.viewmodel.MainTab
import com.example.ui.viewmodel.ScreenRoute

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            val vm: CryptoScopeViewModel = viewModel()
            val uiState by vm.uiState.collectAsState()
            CryptoScopeTheme(darkTheme = uiState.isDarkTheme) {
                CryptoScopeApp(viewModel = vm)
            }
        }
    }
}

@Composable
fun CryptoScopeApp(viewModel: CryptoScopeViewModel) {
    val uiState by viewModel.uiState.collectAsState()
    val isDark = uiState.isDarkTheme
    val bgColor = if (isDark) DarkBackground else LightBackground
    val cardColor = if (isDark) DarkSurface else LightSurface
    val borderColor = if (isDark) DarkBorder else LightBorder

    // Android back handler
    BackHandler(enabled = uiState.currentRoute != ScreenRoute.MAIN && uiState.currentRoute != ScreenRoute.SPLASH) {
        if (!viewModel.navigateBack()) {
            if (uiState.currentRoute != ScreenRoute.MAIN) {
                viewModel.navigateTo(ScreenRoute.MAIN)
            }
        }
    }

    Scaffold(
        modifier = Modifier
            .fillMaxSize()
            .background(bgColor),
        bottomBar = {
            if (uiState.currentRoute == ScreenRoute.MAIN) {
                CryptoScopeBottomBar(
                    activeTab = uiState.activeTab,
                    onTabSelected = { viewModel.selectTab(it) },
                    isDark = isDark,
                    cardColor = cardColor,
                    borderColor = borderColor
                )
            }
        },
        containerColor = bgColor,
        contentWindowInsets = WindowInsets.systemBars
    ) { innerPadding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .background(bgColor)
        ) {
            Crossfade(targetState = uiState.currentRoute, label = "screen_transition") { route ->
                when (route) {
                    ScreenRoute.SPLASH -> SplashScreen(viewModel = viewModel)
                    ScreenRoute.ONBOARDING -> OnboardingScreen(viewModel = viewModel)
                    ScreenRoute.SIGN_IN -> SignInScreen(viewModel = viewModel)
                    ScreenRoute.MAIN -> {
                        when (uiState.activeTab) {
                            MainTab.HOME -> HomeScreen(viewModel = viewModel)
                            MainTab.MARKETS -> MarketsScreen(viewModel = viewModel)
                            MainTab.ORDER_FLOW, MainTab.AI -> AIPredictionScreen(viewModel = viewModel)
                            MainTab.NEWS -> NewsScreen(viewModel = viewModel)
                            MainTab.USER_CENTER, MainTab.MORE -> UserCenterScreen(viewModel = viewModel)
                            MainTab.ALERTS -> AlertsScreen(viewModel = viewModel)
                        }
                    }
                    ScreenRoute.ASSET_DETAIL -> AssetDetailScreen(viewModel = viewModel)
                    ScreenRoute.FEAR_AND_GREED_DETAIL -> FearAndGreedScreen(viewModel = viewModel)
                    ScreenRoute.LIQUIDATION_MAP, ScreenRoute.LIQUIDATION_HEATMAP -> LiquidationsScreen(viewModel = viewModel)
                    ScreenRoute.EDIT_PROFILE -> EditProfileScreen(viewModel = viewModel)
                    ScreenRoute.NEWS_DETAIL -> NewsScreen(viewModel = viewModel)
                    ScreenRoute.CREATE_ALERT -> CreateAlertScreen(viewModel = viewModel)
                    ScreenRoute.ALERT_DETAIL -> AlertDetailScreen(viewModel = viewModel)
                    ScreenRoute.PAPER_DASHBOARD -> PaperDashboardScreen(viewModel = viewModel)
                    ScreenRoute.PAPER_ORDER_TICKET -> PaperOrderTicketScreen(viewModel = viewModel)
                    ScreenRoute.PAPER_POSITION_DETAIL -> PaperPositionDetailScreen(viewModel = viewModel)
                    ScreenRoute.PREDICTION_HISTORY -> PredictionHistoryScreen(viewModel = viewModel)
                    ScreenRoute.PREDICTION_INSPECTOR -> PredictionInspectorScreen(viewModel = viewModel)
                    ScreenRoute.MODEL_PERFORMANCE -> ModelPerformanceScreen(viewModel = viewModel)
                    ScreenRoute.SYSTEM_HEALTH -> SystemHealthScreen(viewModel = viewModel)
                    ScreenRoute.NOTIFICATIONS -> NotificationsScreen(viewModel = viewModel)
                    ScreenRoute.GLOBAL_SEARCH -> GlobalSearchScreen(viewModel = viewModel)
                    ScreenRoute.PROFILE -> UserCenterScreen(viewModel = viewModel)
                    ScreenRoute.SETTINGS -> SettingsScreen(viewModel = viewModel)
                    ScreenRoute.SECURITY -> SecurityScreen(viewModel = viewModel)
                    ScreenRoute.ABOUT_RISK -> AboutRiskScreen(viewModel = viewModel)
                    ScreenRoute.DATA_UNAVAILABLE, ScreenRoute.ETF_FLOW, ScreenRoute.FUNDING_HEATMAP, ScreenRoute.AGGREGATED_ORDERBOOK -> LiquidationsScreen(viewModel = viewModel)
                }
            }
        }
    }
}

@Composable
fun CryptoScopeBottomBar(
    activeTab: MainTab,
    onTabSelected: (MainTab) -> Unit,
    isDark: Boolean,
    cardColor: Color,
    borderColor: Color
) {
    val activeColor = BrandBlue
    val inactiveColor = if (isDark) DarkTextMuted else LightTextMuted

    NavigationBar(
        containerColor = cardColor,
        contentColor = activeColor,
        tonalElevation = 0.dp,
        modifier = Modifier
            .fillMaxWidth()
            .border(BorderStroke(0.5.dp, borderColor))
            .testTag("bottom_nav_bar")
    ) {
        val items = listOf(
            NavTabItem(MainTab.HOME, "Home", Icons.Default.Home),
            NavTabItem(MainTab.MARKETS, "Markets", Icons.Default.ShowChart),
            NavTabItem(MainTab.ORDER_FLOW, "OrderFlow", Icons.Default.QueryStats, hasAiBadge = true),
            NavTabItem(MainTab.NEWS, "News", Icons.Default.Article),
            NavTabItem(MainTab.USER_CENTER, "User Center", Icons.Default.Person)
        )

        items.forEach { tabItem ->
            val selected = activeTab == tabItem.tab || (tabItem.tab == MainTab.ORDER_FLOW && activeTab == MainTab.AI) || (tabItem.tab == MainTab.USER_CENTER && activeTab == MainTab.MORE)
            NavigationBarItem(
                selected = selected,
                onClick = { onTabSelected(tabItem.tab) },
                icon = {
                    Box(contentAlignment = Alignment.TopEnd) {
                        Icon(
                            imageVector = tabItem.icon,
                            contentDescription = tabItem.label,
                            modifier = Modifier.size(22.dp),
                            tint = if (selected) activeColor else inactiveColor
                        )
                        if (tabItem.hasAiBadge) {
                            Surface(
                                shape = RoundedCornerShape(4.dp),
                                color = BrandPurpleAI,
                                modifier = Modifier.offset(x = 12.dp, y = (-6).dp)
                            ) {
                                Text(
                                    text = "+AI",
                                    fontSize = 7.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = Color.White,
                                    modifier = Modifier.padding(horizontal = 2.dp, vertical = 1.dp)
                                )
                            }
                        }
                    }
                },
                label = {
                    Text(
                        text = tabItem.label,
                        fontSize = 10.sp,
                        fontWeight = if (selected) FontWeight.Bold else FontWeight.Normal,
                        color = if (selected) activeColor else inactiveColor
                    )
                },
                colors = NavigationBarItemDefaults.colors(
                    indicatorColor = Color.Transparent,
                    selectedIconColor = activeColor,
                    unselectedIconColor = inactiveColor,
                    selectedTextColor = activeColor,
                    unselectedTextColor = inactiveColor
                ),
                modifier = Modifier.testTag("nav_item_${tabItem.label.lowercase().replace(" ", "_")}")
            )
        }
    }
}

data class NavTabItem(
    val tab: MainTab,
    val label: String,
    val icon: ImageVector,
    val hasAiBadge: Boolean = false
)

