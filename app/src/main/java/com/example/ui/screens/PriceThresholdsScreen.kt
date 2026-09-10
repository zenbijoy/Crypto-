package com.example.ui.screens

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalSoftwareKeyboardController
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.core.database.PriceThresholdEntity
import com.example.ui.theme.*
import com.example.ui.viewmodel.CryptoScopeViewModel
import java.text.NumberFormat
import java.util.Locale

/**
 * Screen providing a dedicated UI form for setting target price thresholds
 * for specific crypto assets backed by Room persistence and real-time prices.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PriceThresholdsScreen(viewModel: CryptoScopeViewModel) {
    val uiState by viewModel.uiState.collectAsState()
    val isDark = uiState.isDarkTheme
    val bgColor = if (isDark) DarkBackground else LightBackground
    val cardColor = if (isDark) DarkSurface else LightSurface
    val borderColor = if (isDark) DarkBorder else LightBorder
    val textColor = if (isDark) DarkTextPrimary else LightTextPrimary
    val textMutedColor = if (isDark) DarkTextMuted else LightTextMuted

    val livePrices by viewModel.repository.livePrices.collectAsState()
    val thresholds by viewModel.repository.getAllPriceThresholds().collectAsState(initial = emptyList())

    val keyboardController = LocalSoftwareKeyboardController.current

    // Form inputs state
    val availableAssets = listOf("BTC", "ETH", "SOL", "BNB", "XRP", "DOGE", "AVAX", "SUI", "LINK", "ADA")
    var selectedAsset by remember { mutableStateOf("BTC") }
    var targetPriceInput by remember { mutableStateOf("") }
    var selectedCondition by remember { mutableStateOf("ABOVE") } // "ABOVE" or "BELOW"
    var noteInput by remember { mutableStateOf("") }
    var errorMessage by remember { mutableStateOf<String?>(null) }
    var successNotification by remember { mutableStateOf<String?>(null) }

    val currentMarketPrice = remember(selectedAsset, livePrices) {
        livePrices["${selectedAsset}USDT"] ?: livePrices[selectedAsset] ?: 0.0
    }

    // Quick percentage target buttons based on current price
    fun setTargetByOffset(percent: Double) {
        if (currentMarketPrice > 0) {
            val calcPrice = currentMarketPrice * (1.0 + percent / 100.0)
            targetPriceInput = String.format(Locale.US, "%.2f", calcPrice)
            selectedCondition = if (percent >= 0) "ABOVE" else "BELOW"
            errorMessage = null
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(bgColor)
            .padding(horizontal = 16.dp)
            .testTag("price_thresholds_screen")
    ) {
        Spacer(modifier = Modifier.height(12.dp))

        // Top Header
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            IconButton(
                onClick = { viewModel.navigateBack() },
                modifier = Modifier
                    .size(36.dp)
                    .testTag("back_button")
            ) {
                Icon(
                    imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                    contentDescription = "Back",
                    tint = textColor
                )
            }
            Spacer(modifier = Modifier.width(8.dp))
            Column {
                Text(
                    text = "Price Threshold Alerts",
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold,
                    color = textColor
                )
                Text(
                    text = "Local Room-Persisted Target Monitoring",
                    fontSize = 11.sp,
                    color = textMutedColor
                )
            }
        }

        Spacer(modifier = Modifier.height(14.dp))

        LazyColumn(
            modifier = Modifier.fillMaxSize(),
            verticalArrangement = Arrangement.spacedBy(14.dp),
            contentPadding = PaddingValues(bottom = 32.dp)
        ) {
            // Form Card
            item {
                Surface(
                    shape = RoundedCornerShape(14.dp),
                    color = cardColor,
                    border = BorderStroke(1.dp, borderColor),
                    modifier = Modifier
                        .fillMaxWidth()
                        .testTag("price_threshold_form")
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.SpaceBetween,
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Text(
                                text = "Set Target Price Threshold",
                                fontSize = 14.sp,
                                fontWeight = FontWeight.Bold,
                                color = textColor
                            )
                            if (currentMarketPrice > 0) {
                                Text(
                                    text = "Live: $${NumberFormat.getNumberInstance(Locale.US).format(currentMarketPrice)}",
                                    fontSize = 11.sp,
                                    fontWeight = FontWeight.SemiBold,
                                    color = BrandBlue,
                                    fontFamily = FontFamily.Monospace
                                )
                            }
                        }

                        Spacer(modifier = Modifier.height(12.dp))

                        // Asset Selector Chips
                        Text(
                            text = "SELECT CRYPTO ASSET",
                            fontSize = 10.sp,
                            fontWeight = FontWeight.Bold,
                            color = textMutedColor,
                            letterSpacing = 0.5.sp
                        )
                        Spacer(modifier = Modifier.height(6.dp))
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(6.dp)
                        ) {
                            availableAssets.take(5).forEach { asset ->
                                val isSelected = selectedAsset == asset
                                Surface(
                                    shape = RoundedCornerShape(8.dp),
                                    color = if (isSelected) BrandBlue else (if (isDark) DarkSurfaceRaised else LightSurfaceRaised),
                                    border = BorderStroke(1.dp, if (isSelected) BrandBlue else borderColor),
                                    modifier = Modifier
                                        .weight(1f)
                                        .clickable {
                                            selectedAsset = asset
                                            errorMessage = null
                                        }
                                        .testTag("asset_chip_$asset")
                                ) {
                                    Box(
                                        contentAlignment = Alignment.Center,
                                        modifier = Modifier.padding(vertical = 8.dp)
                                    ) {
                                        Text(
                                            text = asset,
                                            fontSize = 12.sp,
                                            fontWeight = FontWeight.Bold,
                                            color = if (isSelected) Color.White else textColor
                                        )
                                    }
                                }
                            }
                        }

                        Spacer(modifier = Modifier.height(6.dp))
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(6.dp)
                        ) {
                            availableAssets.drop(5).take(5).forEach { asset ->
                                val isSelected = selectedAsset == asset
                                Surface(
                                    shape = RoundedCornerShape(8.dp),
                                    color = if (isSelected) BrandBlue else (if (isDark) DarkSurfaceRaised else LightSurfaceRaised),
                                    border = BorderStroke(1.dp, if (isSelected) BrandBlue else borderColor),
                                    modifier = Modifier
                                        .weight(1f)
                                        .clickable {
                                            selectedAsset = asset
                                            errorMessage = null
                                        }
                                        .testTag("asset_chip_$asset")
                                ) {
                                    Box(
                                        contentAlignment = Alignment.Center,
                                        modifier = Modifier.padding(vertical = 8.dp)
                                    ) {
                                        Text(
                                            text = asset,
                                            fontSize = 12.sp,
                                            fontWeight = FontWeight.Bold,
                                            color = if (isSelected) Color.White else textColor
                                        )
                                    }
                                }
                            }
                        }

                        Spacer(modifier = Modifier.height(14.dp))

                        // Target Price Input Field
                        Text(
                            text = "TARGET PRICE (USD)",
                            fontSize = 10.sp,
                            fontWeight = FontWeight.Bold,
                            color = textMutedColor,
                            letterSpacing = 0.5.sp
                        )
                        Spacer(modifier = Modifier.height(6.dp))
                        OutlinedTextField(
                            value = targetPriceInput,
                            onValueChange = {
                                targetPriceInput = it
                                errorMessage = null
                            },
                            placeholder = {
                                Text(
                                    text = if (currentMarketPrice > 0) "${currentMarketPrice * 1.05}" else "0.00",
                                    color = textMutedColor,
                                    fontSize = 14.sp
                                )
                            },
                            leadingIcon = {
                                Text(
                                    text = "$",
                                    fontSize = 14.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = BrandBlue,
                                    modifier = Modifier.padding(start = 12.dp)
                                )
                            },
                            singleLine = true,
                            keyboardOptions = KeyboardOptions(
                                keyboardType = KeyboardType.Decimal,
                                imeAction = ImeAction.Next
                            ),
                            colors = OutlinedTextFieldDefaults.colors(
                                focusedBorderColor = BrandBlue,
                                unfocusedBorderColor = borderColor,
                                focusedTextColor = textColor,
                                unfocusedTextColor = textColor
                            ),
                            shape = RoundedCornerShape(10.dp),
                            modifier = Modifier
                                .fillMaxWidth()
                                .testTag("target_price_input")
                        )

                        Spacer(modifier = Modifier.height(8.dp))

                        // Quick Price Offsets
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(6.dp)
                        ) {
                            listOf(
                                "-5%" to -5.0,
                                "-2%" to -2.0,
                                "+2%" to 2.0,
                                "+5%" to 5.0,
                                "+10%" to 10.0
                            ).forEach { (label, pct) ->
                                Surface(
                                    shape = RoundedCornerShape(6.dp),
                                    color = if (isDark) DarkSurfaceRaised else LightSurfaceRaised,
                                    border = BorderStroke(1.dp, borderColor),
                                    modifier = Modifier
                                        .weight(1f)
                                        .clickable { setTargetByOffset(pct) }
                                ) {
                                    Text(
                                        text = label,
                                        fontSize = 10.sp,
                                        fontWeight = FontWeight.SemiBold,
                                        color = if (pct > 0) SemanticPositive else SemanticNegative,
                                        modifier = Modifier.padding(vertical = 4.dp, horizontal = 2.dp),
                                        lineHeight = 12.sp
                                    )
                                }
                            }
                        }

                        Spacer(modifier = Modifier.height(14.dp))

                        // Trigger Condition Selector (Above / Below)
                        Text(
                            text = "TRIGGER CONDITION",
                            fontSize = 10.sp,
                            fontWeight = FontWeight.Bold,
                            color = textMutedColor,
                            letterSpacing = 0.5.sp
                        )
                        Spacer(modifier = Modifier.height(6.dp))
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(10.dp)
                        ) {
                            // Above
                            Surface(
                                shape = RoundedCornerShape(10.dp),
                                color = if (selectedCondition == "ABOVE") SemanticPositiveLight else (if (isDark) DarkSurfaceRaised else LightSurfaceRaised),
                                border = BorderStroke(1.5.dp, if (selectedCondition == "ABOVE") SemanticPositive else borderColor),
                                modifier = Modifier
                                    .weight(1f)
                                    .clickable { selectedCondition = "ABOVE" }
                                    .testTag("condition_above")
                            ) {
                                Row(
                                    modifier = Modifier.padding(12.dp),
                                    verticalAlignment = Alignment.CenterVertically,
                                    horizontalArrangement = Arrangement.Center
                                ) {
                                    Icon(
                                        imageVector = Icons.Default.ArrowUpward,
                                        contentDescription = null,
                                        tint = if (selectedCondition == "ABOVE") SemanticPositive else textMutedColor,
                                        modifier = Modifier.size(16.dp)
                                    )
                                    Spacer(modifier = Modifier.width(6.dp))
                                    Text(
                                        text = "Price Rises Above (≥)",
                                        fontSize = 12.sp,
                                        fontWeight = FontWeight.Bold,
                                        color = if (selectedCondition == "ABOVE") SemanticPositive else textColor
                                    )
                                }
                            }

                            // Below
                            Surface(
                                shape = RoundedCornerShape(10.dp),
                                color = if (selectedCondition == "BELOW") SemanticNegativeLight else (if (isDark) DarkSurfaceRaised else LightSurfaceRaised),
                                border = BorderStroke(1.5.dp, if (selectedCondition == "BELOW") SemanticNegative else borderColor),
                                modifier = Modifier
                                    .weight(1f)
                                    .clickable { selectedCondition = "BELOW" }
                                    .testTag("condition_below")
                            ) {
                                Row(
                                    modifier = Modifier.padding(12.dp),
                                    verticalAlignment = Alignment.CenterVertically,
                                    horizontalArrangement = Arrangement.Center
                                ) {
                                    Icon(
                                        imageVector = Icons.Default.ArrowDownward,
                                        contentDescription = null,
                                        tint = if (selectedCondition == "BELOW") SemanticNegative else textMutedColor,
                                        modifier = Modifier.size(16.dp)
                                    )
                                    Spacer(modifier = Modifier.width(6.dp))
                                    Text(
                                        text = "Price Drops Below (≤)",
                                        fontSize = 12.sp,
                                        fontWeight = FontWeight.Bold,
                                        color = if (selectedCondition == "BELOW") SemanticNegative else textColor
                                    )
                                }
                            }
                        }

                        Spacer(modifier = Modifier.height(14.dp))

                        // Optional Note Input
                        Text(
                            text = "OPTIONAL NOTE / TRADE THESIS",
                            fontSize = 10.sp,
                            fontWeight = FontWeight.Bold,
                            color = textMutedColor,
                            letterSpacing = 0.5.sp
                        )
                        Spacer(modifier = Modifier.height(6.dp))
                        OutlinedTextField(
                            value = noteInput,
                            onValueChange = { noteInput = it },
                            placeholder = {
                                Text(
                                    text = "e.g., Take profit target, Breakout confirmation level",
                                    color = textMutedColor,
                                    fontSize = 12.sp
                                )
                            },
                            singleLine = true,
                            keyboardOptions = KeyboardOptions(imeAction = ImeAction.Done),
                            keyboardActions = KeyboardActions(onDone = { keyboardController?.hide() }),
                            colors = OutlinedTextFieldDefaults.colors(
                                focusedBorderColor = BrandBlue,
                                unfocusedBorderColor = borderColor,
                                focusedTextColor = textColor,
                                unfocusedTextColor = textColor
                            ),
                            shape = RoundedCornerShape(10.dp),
                            modifier = Modifier
                                .fillMaxWidth()
                                .testTag("threshold_note_input")
                        )

                        if (errorMessage != null) {
                            Spacer(modifier = Modifier.height(8.dp))
                            Text(
                                text = errorMessage!!,
                                fontSize = 12.sp,
                                color = SemanticNegative,
                                fontWeight = FontWeight.Medium
                            )
                        }

                        if (successNotification != null) {
                            Spacer(modifier = Modifier.height(8.dp))
                            Text(
                                text = successNotification!!,
                                fontSize = 12.sp,
                                color = SemanticPositive,
                                fontWeight = FontWeight.Medium
                            )
                        }

                        Spacer(modifier = Modifier.height(16.dp))

                        // Submit Button
                        Button(
                            onClick = {
                                val parsedPrice = targetPriceInput.toDoubleOrNull()
                                if (parsedPrice == null || parsedPrice <= 0.0) {
                                    errorMessage = "Please enter a valid positive target price"
                                    return@Button
                                }

                                viewModel.savePriceThreshold(
                                    assetSymbol = selectedAsset,
                                    targetPrice = parsedPrice,
                                    condition = selectedCondition,
                                    note = noteInput
                                )

                                successNotification = "Threshold saved for $selectedAsset at $${parsedPrice}"
                                targetPriceInput = ""
                                noteInput = ""
                                errorMessage = null
                                keyboardController?.hide()
                            },
                            colors = ButtonDefaults.buttonColors(
                                containerColor = BrandBlue,
                                contentColor = Color.White
                            ),
                            shape = RoundedCornerShape(10.dp),
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(46.dp)
                                .testTag("save_threshold_button")
                        ) {
                            Icon(
                                imageVector = Icons.Default.NotificationsActive,
                                contentDescription = null,
                                modifier = Modifier.size(16.dp)
                            )
                            Spacer(modifier = Modifier.width(6.dp))
                            Text(
                                text = "SAVE PRICE THRESHOLD",
                                fontSize = 12.sp,
                                fontWeight = FontWeight.Bold,
                                letterSpacing = 0.5.sp
                            )
                        }
                    }
                }
            }

            // Saved Thresholds Header
            item {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "Saved Thresholds (${thresholds.size})",
                        fontSize = 15.sp,
                        fontWeight = FontWeight.Bold,
                        color = textColor
                    )
                    Text(
                        text = "Room SQLite Database",
                        fontSize = 11.sp,
                        color = textMutedColor
                    )
                }
            }

            // List of Saved Thresholds
            if (thresholds.isEmpty()) {
                item {
                    Surface(
                        shape = RoundedCornerShape(12.dp),
                        color = cardColor,
                        border = BorderStroke(1.dp, borderColor),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Box(
                            modifier = Modifier.padding(24.dp),
                            contentAlignment = Alignment.Center
                        ) {
                            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                                Icon(
                                    imageVector = Icons.Default.AlarmOff,
                                    contentDescription = null,
                                    tint = textMutedColor,
                                    modifier = Modifier.size(36.dp)
                                )
                                Spacer(modifier = Modifier.height(8.dp))
                                Text(
                                    text = "No price thresholds configured yet.",
                                    fontSize = 13.sp,
                                    color = textMutedColor
                                )
                                Text(
                                    text = "Use the form above to add target alerts.",
                                    fontSize = 11.sp,
                                    color = textMutedColor.copy(alpha = 0.8f)
                                )
                            }
                        }
                    }
                }
            } else {
                items(thresholds, key = { it.id }) { threshold ->
                    PriceThresholdCard(
                        threshold = threshold,
                        currentPrice = livePrices["${threshold.assetSymbol}USDT"] ?: livePrices[threshold.assetSymbol] ?: 0.0,
                        cardColor = cardColor,
                        borderColor = borderColor,
                        textColor = textColor,
                        textMutedColor = textMutedColor,
                        isDark = isDark,
                        onToggleActive = {
                            viewModel.togglePriceThresholdActive(threshold.id, threshold.isActive)
                        },
                        onDelete = {
                            viewModel.deletePriceThreshold(threshold.id)
                        }
                    )
                }
            }
        }
    }
}

@Composable
private fun PriceThresholdCard(
    threshold: PriceThresholdEntity,
    currentPrice: Double,
    cardColor: Color,
    borderColor: Color,
    textColor: Color,
    textMutedColor: Color,
    isDark: Boolean,
    onToggleActive: () -> Unit,
    onDelete: () -> Unit
) {
    val isAbove = threshold.condition == "ABOVE"
    val isTriggered = if (currentPrice > 0) {
        if (isAbove) currentPrice >= threshold.targetPrice else currentPrice <= threshold.targetPrice
    } else {
        threshold.isTriggered
    }

    val conditionColor: Color = if (isAbove) SemanticPositive else SemanticNegative
    val distancePct = if (currentPrice > 0) {
        ((threshold.targetPrice - currentPrice) / currentPrice) * 100.0
    } else {
        0.0
    }

    Surface(
        shape = RoundedCornerShape(12.dp),
        color = cardColor,
        border = BorderStroke(
            1.dp,
            if (isTriggered && threshold.isActive) conditionColor else borderColor
        ),
        modifier = Modifier
            .fillMaxWidth()
            .testTag("threshold_item_${threshold.id}")
    ) {
        Column(modifier = Modifier.padding(14.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    // Asset Icon Badge
                    Box(
                        modifier = Modifier
                            .size(36.dp)
                            .clip(CircleShape)
                            .background(BrandBlue.copy(alpha = 0.15f))
                            .border(1.dp, BrandBlue.copy(alpha = 0.3f), CircleShape),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            text = threshold.assetSymbol.take(3),
                            fontSize = 11.sp,
                            fontWeight = FontWeight.Bold,
                            color = BrandBlue
                        )
                    }
                    Spacer(modifier = Modifier.width(10.dp))
                    Column {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Text(
                                text = "${threshold.assetSymbol}/USDT",
                                fontSize = 14.sp,
                                fontWeight = FontWeight.Bold,
                                color = textColor
                            )
                            Spacer(modifier = Modifier.width(6.dp))
                            Surface(
                                shape = RoundedCornerShape(4.dp),
                                color = if (isAbove) SemanticPositiveLight else SemanticNegativeLight
                            ) {
                                Text(
                                    text = if (isAbove) "≥ ABOVE" else "≤ BELOW",
                                    fontSize = 9.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = conditionColor,
                                    modifier = Modifier.padding(horizontal = 4.dp, vertical = 2.dp)
                                )
                            }
                        }

                        if (threshold.note != null) {
                            Text(
                                text = threshold.note,
                                fontSize = 11.sp,
                                color = textMutedColor
                            )
                        }
                    }
                }

                // Switch and Delete Icon
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Switch(
                        checked = threshold.isActive,
                        onCheckedChange = { onToggleActive() },
                        modifier = Modifier.testTag("toggle_threshold_${threshold.id}")
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    IconButton(
                        onClick = onDelete,
                        modifier = Modifier
                            .size(32.dp)
                            .testTag("delete_threshold_${threshold.id}")
                    ) {
                        Icon(
                            imageVector = Icons.Default.DeleteOutline,
                            contentDescription = "Delete Threshold",
                            tint = SemanticNegative.copy(alpha = 0.8f),
                            modifier = Modifier.size(18.dp)
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(10.dp))

            // Metrics row: Target Price vs Current Price vs Distance
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(
                        if (isDark) DarkSurfaceRaised else LightSurfaceRaised,
                        RoundedCornerShape(8.dp)
                    )
                    .padding(horizontal = 10.dp, vertical = 8.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text("TARGET PRICE", fontSize = 9.sp, color = textMutedColor, fontWeight = FontWeight.Bold)
                    Text(
                        text = "$${NumberFormat.getNumberInstance(Locale.US).format(threshold.targetPrice)}",
                        fontSize = 13.sp,
                        fontWeight = FontWeight.Bold,
                        color = textColor,
                        fontFamily = FontFamily.Monospace
                    )
                }

                Column {
                    Text("CURRENT PRICE", fontSize = 9.sp, color = textMutedColor, fontWeight = FontWeight.Bold)
                    Text(
                        text = if (currentPrice > 0) "$${NumberFormat.getNumberInstance(Locale.US).format(currentPrice)}" else "--",
                        fontSize = 13.sp,
                        fontWeight = FontWeight.SemiBold,
                        color = textColor,
                        fontFamily = FontFamily.Monospace
                    )
                }

                Column(horizontalAlignment = Alignment.End) {
                    Text("DISTANCE", fontSize = 9.sp, color = textMutedColor, fontWeight = FontWeight.Bold)
                    Text(
                        text = "${if (distancePct > 0) "+" else ""}${String.format(Locale.US, "%.2f", distancePct)}%",
                        fontSize = 12.sp,
                        fontWeight = FontWeight.Bold,
                        color = if (isTriggered) conditionColor else textColor,
                        fontFamily = FontFamily.Monospace
                    )
                }
            }

            if (isTriggered && threshold.isActive) {
                Spacer(modifier = Modifier.height(6.dp))
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    modifier = Modifier.padding(start = 2.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.CheckCircle,
                        contentDescription = null,
                        tint = conditionColor,
                        modifier = Modifier.size(12.dp)
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text(
                        text = "Threshold crossed! Price target achieved.",
                        fontSize = 11.sp,
                        color = conditionColor,
                        fontWeight = FontWeight.SemiBold
                    )
                }
            }
        }
    }
}
