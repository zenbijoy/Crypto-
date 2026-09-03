package com.example.ui.screens

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Search
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.core.model.AssetSymbol
import com.example.ui.theme.*
import com.example.ui.viewmodel.AssetDetailTab
import com.example.ui.viewmodel.CryptoScopeViewModel
import com.example.ui.viewmodel.ScreenRoute

@Composable
fun GlobalSearchScreen(viewModel: CryptoScopeViewModel) {
    val uiState by viewModel.uiState.collectAsState()
    val isDark = uiState.isDarkTheme
    val bgColor = if (isDark) DarkBackground else LightBackground
    val cardColor = if (isDark) DarkSurface else LightSurface
    val borderColor = if (isDark) DarkBorder else LightBorder
    val textColor = if (isDark) DarkTextPrimary else LightTextPrimary
    val textMutedColor = if (isDark) DarkTextMuted else LightTextMuted

    var query by remember { mutableStateOf("") }
    val allAssets = listOf(AssetSymbol.BTC, AssetSymbol.ETH, AssetSymbol.SOL, AssetSymbol.BNB, AssetSymbol.XRP, AssetSymbol.DOGE)

    val searchResults = remember(query) {
        if (query.isBlank()) allAssets
        else allAssets.filter {
            it.code.contains(query, ignoreCase = true) ||
            it.assetName.contains(query, ignoreCase = true)
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(bgColor)
            .padding(horizontal = 16.dp)
            .testTag("global_search_screen")
    ) {
        Spacer(modifier = Modifier.height(12.dp))

        // Search Header Bar
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            IconButton(onClick = { viewModel.navigateBack() }, modifier = Modifier.size(32.dp)) {
                Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back", tint = textColor)
            }
            Spacer(modifier = Modifier.width(8.dp))
            OutlinedTextField(
                value = query,
                onValueChange = { query = it },
                modifier = Modifier
                    .weight(1f)
                    .testTag("global_search_input"),
                placeholder = { Text("Search assets, alerts, indicators...", fontSize = 13.sp, color = textMutedColor) },
                leadingIcon = { Icon(Icons.Default.Search, contentDescription = null, tint = textMutedColor, modifier = Modifier.size(18.dp)) },
                trailingIcon = {
                    if (query.isNotEmpty()) {
                        IconButton(onClick = { query = "" }) {
                            Icon(Icons.Default.Close, contentDescription = "Clear", tint = textMutedColor, modifier = Modifier.size(16.dp))
                        }
                    }
                },
                colors = OutlinedTextFieldDefaults.colors(
                    focusedBorderColor = BrandBlue,
                    unfocusedBorderColor = borderColor,
                    focusedContainerColor = cardColor,
                    unfocusedContainerColor = cardColor,
                    focusedTextColor = textColor,
                    unfocusedTextColor = textColor
                ),
                shape = RoundedCornerShape(10.dp),
                singleLine = true
            )
        }

        Spacer(modifier = Modifier.height(16.dp))

        Text(
            text = if (query.isBlank()) "POPULAR ASSETS" else "MATCHING ASSETS",
            fontSize = 11.sp,
            fontWeight = FontWeight.Bold,
            color = textMutedColor,
            letterSpacing = 0.8.sp
        )

        Spacer(modifier = Modifier.height(10.dp))

        LazyColumn(
            verticalArrangement = Arrangement.spacedBy(8.dp),
            contentPadding = PaddingValues(bottom = 60.dp)
        ) {
            items(searchResults) { asset ->
                Surface(
                    shape = RoundedCornerShape(12.dp),
                    color = cardColor,
                    border = BorderStroke(1.dp, borderColor),
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable {
                            viewModel.selectAsset(asset)
                            viewModel.setAssetDetailTab(AssetDetailTab.OVERVIEW)
                            viewModel.navigateTo(ScreenRoute.ASSET_DETAIL)
                        }
                ) {
                    Row(
                        modifier = Modifier.padding(14.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column {
                            Text(text = "${asset.code}/USDT", fontSize = 14.sp, fontWeight = FontWeight.Bold, color = textColor)
                            Text(text = asset.assetName, fontSize = 11.sp, color = textMutedColor)
                        }
                        Column(horizontalAlignment = Alignment.End) {
                            Text(text = "$${String.format("%,.2f", asset.basePrice)}", fontSize = 14.sp, fontWeight = FontWeight.SemiBold, color = textColor)
                            Text(text = "View Intelligence", fontSize = 11.sp, color = BrandBlue)
                        }
                    }
                }
            }
        }
    }
}

