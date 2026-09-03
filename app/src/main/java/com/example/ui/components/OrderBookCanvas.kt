package com.example.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.core.model.OrderBookData
import com.example.ui.theme.*

@Composable
fun OrderBookView(
    orderBook: OrderBookData,
    modifier: Modifier = Modifier
) {
    val maxTotal = maxOf(
        orderBook.asks.maxOfOrNull { it.total } ?: 1.0,
        orderBook.bids.maxOfOrNull { it.total } ?: 1.0
    )

    Column(
        modifier = modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(SurfaceDark)
            .padding(12.dp)
    ) {
        // Table Header
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 6.dp),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Text("Price (USDT)", fontSize = 10.sp, fontWeight = FontWeight.SemiBold, color = TextMuted, modifier = Modifier.weight(1.2f))
            Text("Size", fontSize = 10.sp, fontWeight = FontWeight.SemiBold, color = TextMuted, textAlign = TextAlign.End, modifier = Modifier.weight(1f))
            Text("Total", fontSize = 10.sp, fontWeight = FontWeight.SemiBold, color = TextMuted, textAlign = TextAlign.End, modifier = Modifier.weight(1f))
        }

        // Asks (Sells) in reverse order (highest to lowest)
        orderBook.asks.reversed().forEach { ask ->
            val fillFraction = (ask.total / maxTotal).toFloat().coerceIn(0.05f, 1f)
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(22.dp)
            ) {
                // Background depth bar
                Box(
                    modifier = Modifier
                        .fillMaxHeight()
                        .fillMaxWidth(fillFraction)
                        .align(Alignment.CenterEnd)
                        .background(NegativeSurface)
                )
                Row(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(horizontal = 2.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = String.format("%.1f", ask.price),
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Medium,
                        color = SemanticNegative,
                        modifier = Modifier.weight(1.2f)
                    )
                    Text(
                        text = String.format("%.3f", ask.amount),
                        fontSize = 11.sp,
                        color = TextPrimary,
                        textAlign = TextAlign.End,
                        modifier = Modifier.weight(1f)
                    )
                    Text(
                        text = String.format("%.3f", ask.total),
                        fontSize = 11.sp,
                        color = TextMuted,
                        textAlign = TextAlign.End,
                        modifier = Modifier.weight(1f)
                    )
                }
            }
        }

        // Mid Price / Spread Row
        HorizontalDivider(color = BorderColor, modifier = Modifier.padding(vertical = 4.dp))
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 4.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = String.format("%.1f", orderBook.microprice),
                fontSize = 16.sp,
                fontWeight = FontWeight.Bold,
                color = SemanticPositive
            )
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    text = "Spread ${orderBook.spreadPct}%",
                    fontSize = 10.sp,
                    color = TextMuted
                )
                Spacer(modifier = Modifier.width(6.dp))
                Text(
                    text = "Sync #${orderBook.sequenceNumber.toString().takeLast(6)}",
                    fontSize = 9.sp,
                    color = SemanticInfo
                )
            }
        }
        HorizontalDivider(color = BorderColor, modifier = Modifier.padding(vertical = 4.dp))

        // Bids (Buys)
        orderBook.bids.forEach { bid ->
            val fillFraction = (bid.total / maxTotal).toFloat().coerceIn(0.05f, 1f)
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(22.dp)
            ) {
                // Background depth bar
                Box(
                    modifier = Modifier
                        .fillMaxHeight()
                        .fillMaxWidth(fillFraction)
                        .align(Alignment.CenterEnd)
                        .background(PositiveSurface)
                )
                Row(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(horizontal = 2.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = String.format("%.1f", bid.price),
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Medium,
                        color = SemanticPositive,
                        modifier = Modifier.weight(1.2f)
                    )
                    Text(
                        text = String.format("%.3f", bid.amount),
                        fontSize = 11.sp,
                        color = TextPrimary,
                        textAlign = TextAlign.End,
                        modifier = Modifier.weight(1f)
                    )
                    Text(
                        text = String.format("%.3f", bid.total),
                        fontSize = 11.sp,
                        color = TextMuted,
                        textAlign = TextAlign.End,
                        modifier = Modifier.weight(1f)
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(10.dp))

        // Microstructure bar
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(8.dp))
                .background(SurfaceRaised)
                .padding(10.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text("Spread: ${orderBook.spreadPct}%", fontSize = 11.sp, color = TextMuted)
                Text("Imbalance: +${orderBook.imbalancePct.toInt()}%", fontSize = 11.sp, fontWeight = FontWeight.Bold, color = SemanticPositive)
            }
            Spacer(modifier = Modifier.height(4.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text("Microprice: $${String.format("%.1f", orderBook.microprice)}", fontSize = 11.sp, color = TextPrimary)
                Text("Depth 10bps: $8.7M", fontSize = 11.sp, color = TextMuted)
            }
            Spacer(modifier = Modifier.height(8.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text("BID PRESSURE", fontSize = 9.sp, fontWeight = FontWeight.Bold, color = TextMuted)
                Text("${orderBook.bidPressurePct.toInt()}%", fontSize = 11.sp, fontWeight = FontWeight.Bold, color = SemanticPositive)
            }
            Spacer(modifier = Modifier.height(4.dp))
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(6.dp)
                    .clip(RoundedCornerShape(3.dp))
                    .background(BorderColor)
            ) {
                Box(
                    modifier = Modifier
                        .fillMaxHeight()
                        .fillMaxWidth(orderBook.bidPressurePct.toFloat() / 100f)
                        .background(SemanticPositive)
                )
            }
        }
    }
}
