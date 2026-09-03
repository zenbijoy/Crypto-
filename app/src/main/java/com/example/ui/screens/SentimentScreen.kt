package com.example.ui.screens

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
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
import com.example.ui.components.Sparkline
import com.example.ui.theme.*
import com.example.ui.viewmodel.CryptoScopeViewModel

@Composable
fun SentimentScreen(viewModel: CryptoScopeViewModel) {
    val uiState by viewModel.uiState.collectAsState()
    val sentiment = remember(uiState.selectedAsset) {
        viewModel.repository.getSentiment(uiState.selectedAsset)
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(BackgroundDark)
            .padding(horizontal = 16.dp)
            .verticalScroll(rememberScrollState())
            .testTag("sentiment_screen")
    ) {
        Spacer(modifier = Modifier.height(12.dp))

        // 3-Metric Overview Cards
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Surface(
                shape = RoundedCornerShape(10.dp),
                color = SurfaceDark,
                border = BorderStroke(1.dp, BorderColor),
                modifier = Modifier.weight(1f)
            ) {
                Column(modifier = Modifier.padding(10.dp)) {
                    Text("Sentiment", fontSize = 10.sp, color = TextMuted)
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(sentiment.sentimentState, fontSize = 13.sp, fontWeight = FontWeight.Bold, color = SemanticPositive)
                    Text("+12 net 24h", fontSize = 9.sp, color = TextMuted)
                }
            }

            Surface(
                shape = RoundedCornerShape(10.dp),
                color = SurfaceDark,
                border = BorderStroke(1.dp, BorderColor),
                modifier = Modifier.weight(1f)
            ) {
                Column(modifier = Modifier.padding(10.dp)) {
                    Text("Fear & Greed", fontSize = 10.sp, color = TextMuted)
                    Spacer(modifier = Modifier.height(4.dp))
                    Text("${sentiment.fearGreedScore}", fontSize = 14.sp, fontWeight = FontWeight.Bold, color = BrandGold)
                    Text(sentiment.fearGreedLabel, fontSize = 9.sp, color = BrandGold)
                }
            }

            Surface(
                shape = RoundedCornerShape(10.dp),
                color = SurfaceDark,
                border = BorderStroke(1.dp, BorderColor),
                modifier = Modifier.weight(1f)
            ) {
                Column(modifier = Modifier.padding(10.dp)) {
                    Text("Event risk", fontSize = 10.sp, color = TextMuted)
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(sentiment.eventRisk, fontSize = 14.sp, fontWeight = FontWeight.Bold, color = SemanticPositive)
                    Text("Next CPI 18h", fontSize = 9.sp, color = TextMuted)
                }
            }
        }

        Spacer(modifier = Modifier.height(14.dp))

        // Sentiment Change History
        Surface(
            shape = RoundedCornerShape(14.dp),
            color = SurfaceDark,
            border = BorderStroke(1.dp, BorderColor),
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(modifier = Modifier.padding(14.dp)) {
                Text("Sentiment change (7d)", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = TextPrimary)
                Spacer(modifier = Modifier.height(12.dp))
                Sparkline(
                    data = sentiment.history,
                    modifier = Modifier.fillMaxWidth().height(70.dp),
                    isPositive = true
                )
            }
        }

        Spacer(modifier = Modifier.height(14.dp))

        // News Intelligence Header
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text("News intelligence", fontSize = 13.sp, fontWeight = FontWeight.Bold, color = TextPrimary)
            Text("All", fontSize = 11.sp, color = BrandGold)
        }

        Spacer(modifier = Modifier.height(8.dp))

        // News Cards
        sentiment.newsList.forEach { item ->
            val tagCol = when (item.sentimentTag) {
                "GREEN" -> SemanticPositive
                "RED" -> SemanticNegative
                else -> BrandGold
            }
            val tagBg = when (item.sentimentTag) {
                "GREEN" -> SemanticPositiveLight
                "RED" -> SemanticNegativeLight
                else -> BrandGoldLight
            }

            Surface(
                shape = RoundedCornerShape(12.dp),
                color = SurfaceDark,
                border = BorderStroke(1.dp, BorderColor),
                modifier = Modifier.fillMaxWidth().padding(bottom = 8.dp)
            ) {
                Row(
                    modifier = Modifier.padding(12.dp),
                    verticalAlignment = Alignment.Top
                ) {
                    Surface(
                        shape = RoundedCornerShape(4.dp),
                        color = tagBg,
                        modifier = Modifier.width(44.dp)
                    ) {
                        Text(
                            text = item.sentimentTag,
                            fontSize = 8.sp,
                            fontWeight = FontWeight.Bold,
                            color = tagCol,
                            modifier = Modifier.padding(vertical = 3.dp),
                            letterSpacing = 0.3.sp,
                            textAlign = androidx.compose.ui.text.style.TextAlign.Center
                        )
                    }
                    Spacer(modifier = Modifier.width(10.dp))
                    Column(modifier = Modifier.weight(1f)) {
                        Text(
                            text = item.title,
                            fontSize = 12.sp,
                            fontWeight = FontWeight.SemiBold,
                            color = TextPrimary,
                            lineHeight = 16.sp
                        )
                        Spacer(modifier = Modifier.height(4.dp))
                        Text(
                            text = "${item.source} • Relevance ${(item.relevance * 100).toInt()}%",
                            fontSize = 10.sp,
                            color = TextMuted
                        )
                    }
                    Text(
                        text = item.timeAgo,
                        fontSize = 10.sp,
                        color = TextMuted,
                        modifier = Modifier.padding(start = 6.dp)
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(60.dp))
    }
}
