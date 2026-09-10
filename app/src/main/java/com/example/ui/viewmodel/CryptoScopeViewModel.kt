package com.example.ui.viewmodel

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.example.core.data.CryptoScopeRepository
import com.example.core.database.AlertRuleEntity
import com.example.core.database.CryptoScopeDatabase
import com.example.core.database.PaperPositionEntity
import com.example.core.database.PriceThresholdEntity
import com.example.core.model.*
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch

enum class MainTab {
    HOME,
    MARKETS,
    ORDER_FLOW, // OrderFlow tab with +AI badge
    NEWS,       // News & News Flash tab
    USER_CENTER,// User Center / Profile tab
    AI,         // Alias for compatibility
    ALERTS,     // Alias for compatibility
    MORE        // Alias for compatibility
}

enum class ScreenRoute {
    SPLASH,
    ONBOARDING,
    SIGN_IN,
    SIGN_UP,
    MAIN,
    ASSET_DETAIL,
    FEAR_AND_GREED_DETAIL,
    LIQUIDATION_MAP,
    LIQUIDATION_HEATMAP,
    FUNDING_HEATMAP,
    AGGREGATED_ORDERBOOK,
    ETF_FLOW,
    EDIT_PROFILE,
    NEWS_DETAIL,
    CREATE_ALERT,
    PRICE_THRESHOLDS,
    WATCHLIST,
    ALERT_DETAIL,
    PAPER_DASHBOARD,
    PAPER_ORDER_TICKET,
    PAPER_POSITION_DETAIL,
    PREDICTION_HISTORY,
    PREDICTION_INSPECTOR,
    MODEL_PERFORMANCE,
    SYSTEM_HEALTH,
    NOTIFICATIONS,
    GLOBAL_SEARCH,
    PROFILE,
    SETTINGS,
    SECURITY,
    ABOUT_RISK,
    DATA_UNAVAILABLE
}

enum class AssetDetailTab {
    DERIVATIVES,
    SPOT,
    OVERVIEW,
    HOLDERS,
    CHART,
    BOOK,
    LIQUIDATIONS,
    LEVELS
}

data class UserProfile(
    val nickname: String = "user-135927",
    val uid: String = "135927",
    val bio: String = "Crypto derivatives trader & quant enthusiast.",
    val membership: String = "Normal",
    val membershipExpiry: String = "--",
    val apiKey: String = "--",
    val points: Int = 380,
    val inviteCode: String = "CS8899"
)

data class UiState(
    val currentRoute: ScreenRoute = ScreenRoute.SPLASH,
    val activeTab: MainTab = MainTab.HOME,
    val assetDetailTab: AssetDetailTab = AssetDetailTab.SPOT,
    val selectedAsset: AssetSymbol = AssetSymbol.BTC,
    val selectedHorizon: Horizon = Horizon.H_1H,
    val isOnboardingCompleted: Boolean = false,
    val isAuthenticated: Boolean = true,
    val hasActiveSession: Boolean = true,
    val userProfile: UserProfile = UserProfile(),
    val userName: String = "user-135927",
    val userEmail: String = "user@cryptoscope.ai",
    val isLiveStreaming: Boolean = true,
    val isDarkTheme: Boolean = false,
    val colorPreferenceGreenPositive: Boolean = true,
    val screenshotSharingEnabled: Boolean = true,
    val circuitBreakerTriggered: Boolean = false,
    val searchQuery: String = "",
    val activeAlertDetailId: String = "alert-1",
    val activePositionDetailId: String = "pos-btc-1",
    val activePredictionAuditId: String = "hist-1",
    val selectedWatchlistTab: String = "Default",
    val selectedMarketFilterTab: String = "Derivatives",
    val selectedAlertFilterTab: String = "Active",
    val selectedLanguage: String = "English",
    val watchlist: Set<String> = setOf("BTC", "ETH", "SOL", "AVAX"),
    val floatingPriceAsset: String = "BTC",
    val isFloatingPriceVisible: Boolean = true,
    val paperEquity: Double = 10842.60,
    val paperTotalPnl: Double = 842.60,
    val paperTotalPnlPct: Double = 8.43
)

class CryptoScopeViewModel(application: Application) : AndroidViewModel(application) {
    private val database = CryptoScopeDatabase.getDatabase(application)
    val repository = CryptoScopeRepository(database.dao())

    private val _uiState = MutableStateFlow(UiState())
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    val liveMarkets: StateFlow<List<MarketItem>> = combine(
        repository.livePrices,
        repository.liveTickers,
        repository.liveFundingRates,
        repository.liveOpenInterests
    ) { _, _, _, _ ->
        repository.getMarkets()
    }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), repository.getMarkets())

    val marketOverview = repository.marketOverview
    val liveTickers = repository.liveTickers
    val fearGreedHistory = repository.fearGreedHistory
    val contractRadarAlerts = repository.contractRadarAlerts
    val backendNews = repository.backendNews

    fun getMarkets(): List<MarketItem> = repository.getMarkets()
    fun getPrediction(asset: AssetSymbol = _uiState.value.selectedAsset, horizon: Horizon = _uiState.value.selectedHorizon): PredictionForecast = repository.getPrediction(asset, horizon)
    fun getDerivatives(asset: AssetSymbol = _uiState.value.selectedAsset): DerivativesData = repository.getDerivatives(asset)
    fun getOrderBook(asset: AssetSymbol = _uiState.value.selectedAsset): OrderBookData = repository.getOrderBook(asset)
    fun getSentiment(asset: AssetSymbol = _uiState.value.selectedAsset): SentimentData = repository.getSentiment(asset)
    fun getLiquidations(asset: AssetSymbol = _uiState.value.selectedAsset): LiquidationData = repository.getLiquidations(asset)
    fun getMacro(): MacroData = repository.getMacro()
    fun getCandles(asset: AssetSymbol = _uiState.value.selectedAsset): List<CandleStick> = repository.getCandles(asset)
    fun getNextFundingCountdown(symbol: String = _uiState.value.selectedAsset.code): String = repository.getNextFundingCountdown(symbol)

    // Backstack for natural back navigation
    private val navigationBackstack = mutableListOf<ScreenRoute>()

    init {
        // Collect live price map to trigger smooth recompositions
        viewModelScope.launch {
            repository.livePrices.collect {
                // updates automatically observed
            }
        }

        // Collect and seed Room Watchlist
        viewModelScope.launch {
            repository.getWatchlistSymbols().collect { entities ->
                if (entities.isEmpty()) {
                    listOf("BTC", "ETH", "SOL", "AVAX").forEach { sym ->
                        repository.addWatchlistSymbol(sym)
                    }
                } else {
                    _uiState.update { it.copy(watchlist = entities.map { e -> e.symbol }.toSet()) }
                }
            }
        }

        // Seed default alerts if Room is empty
        viewModelScope.launch {
            repository.getAlertRules().collect { rules ->
                if (rules.isEmpty()) {
                    repository.addAlertRule(
                        AlertRuleEntity(
                            id = "alert-1",
                            asset = "BTC",
                            horizon = "1H",
                            signal = "STRONG LONG",
                            minConfidence = 80,
                            minAgreement = 75,
                            minDataQuality = 95,
                            cooldownMinutes = 15,
                            requireExpectedEdge = true,
                            requireRiskEngineAllow = true,
                            status = "ACTIVE"
                        )
                    )
                    repository.addAlertRule(
                        AlertRuleEntity(
                            id = "alert-2",
                            asset = "SOL",
                            horizon = "15M",
                            signal = "BREAKOUT",
                            minConfidence = 75,
                            minAgreement = 70,
                            minDataQuality = 90,
                            cooldownMinutes = 30,
                            requireExpectedEdge = true,
                            requireRiskEngineAllow = true,
                            status = "ACTIVE"
                        )
                    )
                    repository.addAlertRule(
                        AlertRuleEntity(
                            id = "alert-3",
                            asset = "ETH",
                            horizon = "1H",
                            signal = "OI SPIKE",
                            minConfidence = 70,
                            minAgreement = 65,
                            minDataQuality = 88,
                            cooldownMinutes = 60,
                            requireExpectedEdge = true,
                            requireRiskEngineAllow = true,
                            status = "PAUSED"
                        )
                    )
                }
            }
        }

        // Seed initial price thresholds if Room is empty
        viewModelScope.launch {
            repository.getAllPriceThresholds().collect { thresholds ->
                if (thresholds.isEmpty()) {
                    repository.savePriceThreshold(
                        PriceThresholdEntity(
                            id = "threshold-btc-115k",
                            assetSymbol = "BTC",
                            targetPrice = 115000.0,
                            condition = "ABOVE",
                            note = "Key institutional resistance breakout target",
                            isActive = true
                        )
                    )
                    repository.savePriceThreshold(
                        PriceThresholdEntity(
                            id = "threshold-eth-4200",
                            assetSymbol = "ETH",
                            targetPrice = 4200.0,
                            condition = "BELOW",
                            note = "Major demand zone support level",
                            isActive = true
                        )
                    )
                    repository.savePriceThreshold(
                        PriceThresholdEntity(
                            id = "threshold-sol-220",
                            assetSymbol = "SOL",
                            targetPrice = 220.0,
                            condition = "ABOVE",
                            note = "Momentum expansion continuation level",
                            isActive = true
                        )
                    )
                }
            }
        }

        // Seed initial paper trading position if Room is empty
        viewModelScope.launch {
            repository.getPaperPositions().collect { positions ->
                if (positions.isEmpty()) {
                    repository.addPaperPosition(
                        PaperPositionEntity(
                            id = "pos-initial-btc",
                            symbol = "BTC/USDT",
                            direction = "LONG",
                            entryPrice = 107600.0,
                            markPrice = 109420.30,
                            sizeUsd = 5000.0,
                            leverage = 10,
                            stopLoss = 105448.0,
                            takeProfit = 113500.0,
                            aiConfidence = 84,
                            aiRegime = "Bull trend momentum",
                            aiModel = "btc-1h-v26.4",
                            aiRisk = "LOW"
                        )
                    )
                }
            }
        }
    }

    /**
     * Phase 17 App Startup Flow:
     * Splash -> check onboarding completion -> check Supabase session
     */
    fun handleSplashNavigation() {
        val state = _uiState.value
        when {
            !state.isOnboardingCompleted -> {
                _uiState.update { it.copy(currentRoute = ScreenRoute.ONBOARDING) }
            }
            state.isAuthenticated && state.hasActiveSession -> {
                _uiState.update { it.copy(currentRoute = ScreenRoute.MAIN, activeTab = MainTab.HOME) }
            }
            else -> {
                _uiState.update { it.copy(currentRoute = ScreenRoute.SIGN_IN) }
            }
        }
    }

    fun completeOnboarding() {
        _uiState.update { it.copy(isOnboardingCompleted = true, currentRoute = ScreenRoute.SIGN_IN) }
    }

    fun onSignInSuccess(token: String, email: String) {
        com.example.core.network.client.CryptoApiClient.setAuthToken(token)
        _uiState.update {
            it.copy(
                isAuthenticated = true,
                hasActiveSession = true,
                userEmail = email,
                currentRoute = ScreenRoute.MAIN,
                activeTab = MainTab.HOME
            )
        }
    }

    fun navigateTo(route: ScreenRoute) {
        if (_uiState.value.currentRoute != route) {
            navigationBackstack.add(_uiState.value.currentRoute)
            _uiState.update { it.copy(currentRoute = route) }
        }
    }

    fun navigateBack(): Boolean {
        if (navigationBackstack.isNotEmpty()) {
            val previousRoute = navigationBackstack.removeAt(navigationBackstack.size - 1)
            _uiState.update { it.copy(currentRoute = previousRoute) }
            return true
        }
        return false
    }

    fun selectTab(tab: MainTab) {
        _uiState.update { it.copy(activeTab = tab, currentRoute = ScreenRoute.MAIN) }
    }

    fun selectAsset(asset: AssetSymbol) {
        repository.setSelectedAsset(asset)
        _uiState.update { it.copy(selectedAsset = asset) }
    }

    fun selectHorizon(horizon: Horizon) {
        repository.setSelectedHorizon(horizon)
        _uiState.update { it.copy(selectedHorizon = horizon) }
    }

    fun setAssetDetailTab(tab: AssetDetailTab) {
        _uiState.update { it.copy(assetDetailTab = tab) }
    }

    fun setMarketFilterTab(tab: String) {
        _uiState.update { it.copy(selectedMarketFilterTab = tab) }
    }

    fun setAlertFilterTab(tab: String) {
        _uiState.update { it.copy(selectedAlertFilterTab = tab) }
    }

    fun setSearchQuery(query: String) {
        _uiState.update { it.copy(searchQuery = query) }
    }

    fun toggleDarkTheme() {
        _uiState.update { it.copy(isDarkTheme = !it.isDarkTheme) }
    }

    fun updateProfile(nickname: String, bio: String) {
        _uiState.update {
            it.copy(
                userName = nickname,
                userProfile = it.userProfile.copy(nickname = nickname, bio = bio)
            )
        }
    }

    fun toggleScreenshotSharing() {
        _uiState.update { it.copy(screenshotSharingEnabled = !it.screenshotSharingEnabled) }
    }

    fun toggleColorPreference() {
        _uiState.update { it.copy(colorPreferenceGreenPositive = !it.colorPreferenceGreenPositive) }
    }

    fun setLanguage(language: String) {
        _uiState.update { it.copy(selectedLanguage = language) }
    }

    fun openAlertDetail(alertId: String) {
        _uiState.update { it.copy(activeAlertDetailId = alertId) }
        navigateTo(ScreenRoute.ALERT_DETAIL)
    }

    fun openPositionDetail(positionId: String) {
        _uiState.update { it.copy(activePositionDetailId = positionId) }
        navigateTo(ScreenRoute.PAPER_POSITION_DETAIL)
    }

    fun openPredictionInspector(auditId: String) {
        _uiState.update { it.copy(activePredictionAuditId = auditId) }
        navigateTo(ScreenRoute.PREDICTION_INSPECTOR)
    }

    fun toggleCircuitBreaker() {
        val next = !_uiState.value.circuitBreakerTriggered
        _uiState.update { it.copy(circuitBreakerTriggered = next) }
        repository.toggleCircuitBreaker(next)
    }

    fun toggleLiveConnection() {
        val next = !_uiState.value.isLiveStreaming
        _uiState.update { it.copy(isLiveStreaming = next) }
        repository.toggleLiveConnection(next)
    }

    // Toggle Watchlist / Favorites
    fun toggleWatchlist(symbol: String) {
        viewModelScope.launch {
            val current = _uiState.value.watchlist
            val cleanSymbol = symbol.replace("USDT", "").replace("/", "")
            if (current.contains(cleanSymbol)) {
                repository.removeWatchlistSymbol(cleanSymbol)
                _uiState.update { it.copy(watchlist = current - cleanSymbol) }
            } else {
                repository.addWatchlistSymbol(cleanSymbol)
                _uiState.update { it.copy(watchlist = current + cleanSymbol) }
            }
        }
    }

    fun isFavorite(symbol: String): Boolean {
        val clean = symbol.replace("USDT", "").replace("/", "")
        return _uiState.value.watchlist.contains(clean)
    }

    fun setFloatingPriceAsset(symbol: String) {
        val clean = symbol.replace("USDT", "").replace("/", "")
        _uiState.update { it.copy(floatingPriceAsset = clean, isFloatingPriceVisible = true) }
    }

    fun toggleFloatingPriceVisible() {
        _uiState.update { it.copy(isFloatingPriceVisible = !it.isFloatingPriceVisible) }
    }

    // Place a paper trade order
    fun placePaperOrder(
        symbol: String,
        direction: String,
        sizeUsd: Double,
        stopLossPct: Double,
        takeProfitPct: Double,
        leverage: Int = 10
    ) {
        viewModelScope.launch {
            val cleanSymbol = symbol.replace("/", "")
            val price = repository.livePrices.value[cleanSymbol] 
                ?: repository.livePrices.value["${cleanSymbol}USDT"] 
                ?: 109420.30
            val newPosition = PaperPositionEntity(
                id = "pos-${System.currentTimeMillis()}",
                symbol = symbol,
                direction = direction,
                entryPrice = price,
                markPrice = price,
                sizeUsd = sizeUsd,
                leverage = leverage,
                stopLoss = if (direction == "LONG") price * (1.0 - stopLossPct / 100.0) else price * (1.0 + stopLossPct / 100.0),
                takeProfit = if (direction == "LONG") price * (1.0 + takeProfitPct / 100.0) else price * (1.0 - takeProfitPct / 100.0),
                aiConfidence = 84,
                aiRegime = "Momentum breakout",
                aiModel = "${symbol.take(3).lowercase()}-1h-v26",
                aiRisk = if (leverage > 10) "HIGH" else "MEDIUM"
            )
            repository.addPaperPosition(newPosition)
            navigateTo(ScreenRoute.PAPER_DASHBOARD)
        }
    }

    fun toggleAlertStatus(alertId: String, currentStatus: String) {
        viewModelScope.launch {
            val next = if (currentStatus == "ACTIVE") "PAUSED" else "ACTIVE"
            repository.setAlertStatus(alertId, next)
        }
    }

    // Create a new alert rule
    fun createAlertRule(
        asset: String,
        horizon: String,
        signal: String,
        minConfidence: Int,
        minAgreement: Int,
        minQuality: Int,
        cooldown: Int
    ) {
        viewModelScope.launch {
            val newAlert = AlertRuleEntity(
                id = "alert-${System.currentTimeMillis()}",
                asset = asset,
                horizon = horizon,
                signal = signal,
                minConfidence = minConfidence,
                minAgreement = minAgreement,
                minDataQuality = minQuality,
                cooldownMinutes = cooldown,
                requireExpectedEdge = true,
                requireRiskEngineAllow = true,
                status = "ACTIVE"
            )
            repository.addAlertRule(newAlert)
            navigateTo(ScreenRoute.MAIN)
            selectTab(MainTab.ALERTS)
        }
    }

    fun pauseAlert(alertId: String) {
        viewModelScope.launch {
            repository.setAlertStatus(alertId, "PAUSED")
        }
    }

    fun deleteAlert(alertId: String) {
        viewModelScope.launch {
            repository.removeAlertRule(alertId)
            navigateBack()
        }
    }

    fun closePaperPosition(posId: String) {
        viewModelScope.launch {
            repository.closePaperPosition(posId)
            navigateBack()
        }
    }

    // Price Threshold Form & CRUD Actions
    fun savePriceThreshold(
        assetSymbol: String,
        targetPrice: Double,
        condition: String,
        note: String?
    ) {
        viewModelScope.launch {
            val entity = PriceThresholdEntity(
                id = "thresh-${System.currentTimeMillis()}",
                assetSymbol = assetSymbol.uppercase().trim(),
                targetPrice = targetPrice,
                condition = condition,
                note = note?.takeIf { it.isNotBlank() },
                isActive = true,
                isTriggered = false
            )
            repository.savePriceThreshold(entity)
        }
    }

    fun togglePriceThresholdActive(thresholdId: String, currentActive: Boolean) {
        viewModelScope.launch {
            repository.togglePriceThresholdActive(thresholdId, !currentActive)
        }
    }

    fun deletePriceThreshold(thresholdId: String) {
        viewModelScope.launch {
            repository.deletePriceThreshold(thresholdId)
        }
    }

    fun resetPaperBalance() {
        _uiState.update { it.copy(paperEquity = 10000.0, paperTotalPnl = 0.0, paperTotalPnlPct = 0.0) }
    }

    fun signInSuccess(email: String) {
        _uiState.update { it.copy(isAuthenticated = true, userEmail = email, currentRoute = ScreenRoute.MAIN) }
    }

    fun signOut() {
        _uiState.update { it.copy(isAuthenticated = false, currentRoute = ScreenRoute.SIGN_IN) }
    }
}

