package com.example.core.network.datasource

import com.example.core.network.api.CryptoScopeBackendApiService
import com.example.core.network.client.CryptoApiClient
import com.example.core.network.dto.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

/**
 * Remote data source for CryptoScope AI FastAPI Gateway.
 * Provides fail-safe methods with real-time defaults and structured domain data.
 */
class CryptoScopeBackendRemoteDataSource(
    private val apiService: CryptoScopeBackendApiService = CryptoApiClient.backendApiService
) {

    suspend fun fetchMarketOverview(): Result<MarketOverviewResponseDto> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.getMarketOverview()
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("HTTP ${response.code()} ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun fetchFearGreed(): Result<FearGreedSummaryDto> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.getFearGreed()
            if (response.isSuccessful && response.body() != null) {
                return@withContext Result.success(response.body()!!)
            }
        } catch (_: Exception) {}

        // Direct Real-time fallback to Alternative.me official Fear & Greed API
        try {
            val altRes = CryptoApiClient.alternativeMeApiService.getFearAndGreed(30)
            val list = altRes.body()?.data
            if (altRes.isSuccessful && !list.isNullOrEmpty()) {
                val current = list[0]
                val prev = if (list.size > 1) list[1] else null
                val curVal = current.value.toIntOrNull() ?: 50
                val prevVal = prev?.value?.toIntOrNull() ?: curVal
                val change = curVal - prevVal
                return@withContext Result.success(
                    FearGreedSummaryDto(
                        value = curVal,
                        classification = current.valueClassification,
                        change24h = change,
                        updatedAt = "Just now"
                    )
                )
            }
        } catch (_: Exception) {}

        Result.failure(Exception("Failed to fetch Fear & Greed"))
    }

    suspend fun fetchFearGreedHistory(limit: Int = 30): List<AlternativeMeFngItemDto> = withContext(Dispatchers.IO) {
        try {
            val altRes = CryptoApiClient.alternativeMeApiService.getFearAndGreed(limit)
            val list = altRes.body()?.data
            if (altRes.isSuccessful && !list.isNullOrEmpty()) {
                return@withContext list
            }
        } catch (_: Exception) {}
        emptyList()
    }

    suspend fun fetchEtfOverview(): Result<EtfOverviewDto> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.getEtfOverview()
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("HTTP ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun fetchRankings(type: String = "volume", limit: Int = 50): Result<List<RankingItemDto>> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.getRankings(type = type, limit = limit)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!.items)
            } else {
                Result.failure(Exception("HTTP ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun fetchScreener(): Result<ScreenerResponseDto> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.getScreener()
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("HTTP ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun fetchContractRadar(): Result<List<ContractRadarAlertDto>> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.getContractRadar()
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("HTTP ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun fetchNews(): Result<List<NewsItemDto>> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.getNews()
            if (response.isSuccessful && response.body() != null) {
                val list = response.body()!!
                if (list.isNotEmpty()) {
                    return@withContext Result.success(list)
                }
            }
        } catch (_: Exception) {}

        // Direct Real-time fallback to live crypto news RSS feed
        try {
            val request = okhttp3.Request.Builder()
                .url("https://cointelegraph.com/rss")
                .header("User-Agent", "Mozilla/5.0")
                .build()
            val res = CryptoApiClient.okHttpClient.newCall(request).execute()
            if (res.isSuccessful) {
                val xml = res.body?.string().orEmpty()
                val parsed = parseRssFeed(xml)
                if (parsed.isNotEmpty()) {
                    return@withContext Result.success(parsed)
                }
            }
        } catch (_: Exception) {}

        Result.failure(Exception("Failed to fetch news"))
    }

    private fun parseRssFeed(xml: String): List<NewsItemDto> {
        val items = mutableListOf<NewsItemDto>()
        val itemPattern = java.util.regex.Pattern.compile("<item>(.*?)</item>", java.util.regex.Pattern.DOTALL)
        val titlePattern = java.util.regex.Pattern.compile("<title>(?:<!\\[CDATA\\[)?(.*?)(?:\\]\\]>)?</title>", java.util.regex.Pattern.DOTALL)
        val descPattern = java.util.regex.Pattern.compile("<description>(?:<!\\[CDATA\\[)?(.*?)(?:\\]\\]>)?</description>", java.util.regex.Pattern.DOTALL)
        val linkPattern = java.util.regex.Pattern.compile("<link>(?:<!\\[CDATA\\[)?(.*?)(?:\\]\\]>)?</link>", java.util.regex.Pattern.DOTALL)
        val pubDatePattern = java.util.regex.Pattern.compile("<pubDate>(?:<!\\[CDATA\\[)?(.*?)(?:\\]\\]>)?</pubDate>", java.util.regex.Pattern.DOTALL)
        val catPattern = java.util.regex.Pattern.compile("<category>(?:<!\\[CDATA\\[)?(.*?)(?:\\]\\]>)?</category>", java.util.regex.Pattern.DOTALL)

        val matcher = itemPattern.matcher(xml)
        var idCounter = 1
        while (matcher.find() && items.size < 25) {
            val itemBlock = matcher.group(1) ?: continue
            val tMatcher = titlePattern.matcher(itemBlock)
            val title = if (tMatcher.find()) tMatcher.group(1).orEmpty().trim() else ""
            if (title.isBlank()) continue

            val dMatcher = descPattern.matcher(itemBlock)
            val rawDesc = if (dMatcher.find()) dMatcher.group(1).orEmpty() else ""
            val cleanDesc = rawDesc.replace(Regex("<.*?>"), "").trim()

            val lMatcher = linkPattern.matcher(itemBlock)
            val link = if (lMatcher.find()) lMatcher.group(1).orEmpty().trim() else ""

            val pMatcher = pubDatePattern.matcher(itemBlock)
            val pubDate = if (pMatcher.find()) pMatcher.group(1).orEmpty().trim() else ""

            val cMatcher = catPattern.matcher(itemBlock)
            val cat = if (cMatcher.find()) cMatcher.group(1).orEmpty().trim() else "Market News"

            val isBullish = title.contains("surge", true) || title.contains("rise", true) || title.contains("inflow", true) || title.contains("record", true) || title.contains("high", true)
            val isBearish = title.contains("drop", true) || title.contains("fall", true) || title.contains("crash", true) || title.contains("loss", true) || title.contains("liquidation", true)
            val sentiment = if (isBullish) "BULLISH" else if (isBearish) "BEARISH" else "NEUTRAL"
            val score = if (isBullish) 0.65 else if (isBearish) -0.65 else 0.0

            items.add(
                NewsItemDto(
                    id = "ct-$idCounter",
                    title = title,
                    summary = if (cleanDesc.isNotBlank()) cleanDesc else title,
                    source = "Cointelegraph",
                    category = if (cat.isNotBlank()) cat else "Market News",
                    sentiment = sentiment,
                    sentimentScore = score,
                    publishedAt = pubDate,
                    url = link
                )
            )
            idCounter++
        }
        return items
    }

    suspend fun fetchProvidersStatus(): Result<List<ProviderStatusDto>> = withContext(Dispatchers.IO) {
        try {
            val response = apiService.getProvidersStatus()
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("HTTP ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
