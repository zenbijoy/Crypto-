package com.example.ui.screens

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
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
fun WatchlistScreen(viewModel: CryptoScopeViewModel) {
    val uiState by viewModel.uiState.collectAsState()
    val livePrices by viewModel.repository.livePrices.collectAsState()
    val markets = remember(livePrices) { viewModel.repository.getMarkets() }

    val categories = listOf("Default", "Scalping", "Swing")
    var selectedCat by remember { mutableStateOf("Default") }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(BackgroundDark)
            .padding(horizontal = 16.dp)
            .testTag("watchlist_screen")
    ) {
        Spacer(modifier = Modifier.height(12.dp))

        // Custom lists pills
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            categories.forEach { cat ->
                val isSelected = selectedCat == cat
                Surface(
                    shape = RoundedCornerShape(16.dp),
                    color = if (isSelected) BrandGold else SurfaceRaised,
                    border = BorderStroke(1.dp, if (isSelected) BrandGold else BorderColor),
                    modifier = Modifier.clickable { selectedCat = cat }
                ) {
                    Text(
                        text = cat,
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Bold,
                        color = if (isSelected) BackgroundDark else TextMuted,
                        modifier = Modifier.padding(horizontal = 14.dp, vertical = 5.dp)
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(14.dp))

        // Markets in Watchlist
        LazyColumn(
            verticalArrangement = Arrangement.spacedBy(10.dp),
            modifier = Modifier.weight(1f)
        ) {
            items(markets.take(3), key = { it.symbol }) { market ->
                val isPositive = market.change24h >= 0
                val badgeColor = if (isPositive) SemanticPositive else SemanticNegative
                Surface(
                    shape = RoundedCornerShape(12.dp),
                    color = DarkSurface,
                    border = BorderStroke(1.dp, DarkBorder),
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable {
                            val asset = try {
                                AssetSymbol.valueOf(market.asset)
                            } catch (e: Exception) {
                                AssetSymbol.BTC
                            }
                            viewModel.selectAsset(asset)
                            viewModel.setAssetDetailTab(AssetDetailTab.OVERVIEW)
                            viewModel.navigateTo(ScreenRoute.ASSET_DETAIL)
                        }
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(14.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column {
                            Text(market.asset, fontSize = 14.sp, fontWeight = FontWeight.Bold, color = DarkTextPrimary)
                            Text(market.pair, fontSize = 11.sp, color = DarkTextMuted)
                        }
                        Column(horizontalAlignment = Alignment.End) {
                            Text("$${"%,.2f".format(market.price)}", fontSize = 14.sp, fontWeight = FontWeight.Bold, color = DarkTextPrimary)
                            Text(
                                text = "${if (isPositive) "+" else ""}${"%.2f".format(market.change24h)}%",
                                fontSize = 11.sp,
                                fontWeight = FontWeight.Bold,
                                color = badgeColor
                            )
                        }
                    }
                }
            }

            item {
                OutlinedButton(
                    onClick = { viewModel.navigateTo(ScreenRoute.GLOBAL_SEARCH) },
                    border = BorderStroke(1.dp, BorderColor),
                    shape = RoundedCornerShape(10.dp),
                    modifier = Modifier.fillMaxWidth().height(44.dp)
                ) {
                    Icon(Icons.Default.Add, contentDescription = null, tint = BrandGold, modifier = Modifier.size(16.dp))
                    Spacer(modifier = Modifier.width(6.dp))
                    Text("+ Add market", fontSize = 12.sp, fontWeight = FontWeight.SemiBold, color = BrandGold)
                }
            }

            item {
                Spacer(modifier = Modifier.height(10.dp))
                Text("Quick metrics", fontSize = 13.sp, fontWeight = FontWeight.Bold, color = TextPrimary)
            }

            item {
                Surface(
                    shape = RoundedCornerShape(12.dp),
                    color = SurfaceDark,
                    border = BorderStroke(1.dp, BorderColor),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(modifier = Modifier.padding(14.dp)) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Column {
                                Text("BTC Confidence", fontSize = 10.sp, color = TextMuted)
                                Text("82 / 100", fontSize = 14.sp, fontWeight = FontWeight.Bold, color = BrandGold)
                            }
                            Column(horizontalAlignment = Alignment.End) {
                                Text("ETH Confidence", fontSize = 10.sp, color = TextMuted)
                                Text("61 (No-Trade)", fontSize = 14.sp, fontWeight = FontWeight.Bold, color = TextMuted)
                            }
                        }
                        HorizontalDivider(color = BorderColor, modifier = Modifier.padding(vertical = 8.dp))
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Column {
                                Text("SOL Confidence", fontSize = 10.sp, color = TextMuted)
                                Text("77 / 100", fontSize = 14.sp, fontWeight = FontWeight.Bold, color = SemanticPositive)
                            }
                            Column(horizontalAlignment = Alignment.End) {
                                Text("Event Risk", fontSize = 10.sp, color = TextMuted)
                                Text("Low", fontSize = 14.sp, fontWeight = FontWeight.Bold, color = SemanticPositive)
                            }
                        }
                    }
                }
            }
        }
    }
}
