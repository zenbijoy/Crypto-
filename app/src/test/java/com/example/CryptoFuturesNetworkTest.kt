package com.example

import com.example.core.network.client.CryptoApiClient
import com.example.core.network.dto.*
import com.squareup.moshi.Types
import org.junit.Assert.*
import org.junit.Test

class CryptoFuturesNetworkTest {

    private val moshi = CryptoApiClient.moshi

    @Test
    fun testFutures24HrTickerParsing() {
        val json = """
            {
                "symbol": "BTCUSDT",
                "priceChange": "2450.50",
                "priceChangePercent": "2.35",
                "weightedAvgPrice": "108120.40",
                "lastPrice": "109420.30",
                "lastQty": "0.145",
                "openPrice": "106969.80",
                "highPrice": "110200.00",
                "lowPrice": "106500.00",
                "volume": "45120.50",
                "quoteVolume": "4892015000.00",
                "openTime": 1725180000000,
                "closeTime": 1725266400000,
                "firstId": 10001,
                "lastId": 20002,
                "count": 987654
            }
        """.trimIndent()

        val adapter = moshi.adapter(Futures24HrTickerDto::class.java)
        val dto = adapter.fromJson(json)

        assertNotNull(dto)
        assertEquals("BTCUSDT", dto?.symbol)
        assertEquals("109420.30", dto?.lastPrice)
        assertEquals("2.35", dto?.priceChangePercent)
        assertEquals("4892015000.00", dto?.quoteVolume)
    }

    @Test
    fun testFuturesPremiumIndexParsing() {
        val json = """
            {
                "symbol": "BTCUSDT",
                "markPrice": "109418.90",
                "indexPrice": "109415.20",
                "estimatedSettlePrice": "109419.00",
                "lastFundingRate": "0.00010000",
                "interestRate": "0.00010000",
                "nextFundingTime": 1725292800000,
                "time": 1725266400000
            }
        """.trimIndent()

        val adapter = moshi.adapter(FuturesPremiumIndexDto::class.java)
        val dto = adapter.fromJson(json)

        assertNotNull(dto)
        assertEquals("BTCUSDT", dto?.symbol)
        assertEquals("0.00010000", dto?.lastFundingRate)
        assertEquals("109418.90", dto?.markPrice)
    }

    @Test
    fun testFuturesOpenInterestParsing() {
        val json = """
            {
                "symbol": "BTCUSDT",
                "openInterest": "28540.125",
                "time": 1725266400000
            }
        """.trimIndent()

        val adapter = moshi.adapter(FuturesOpenInterestDto::class.java)
        val dto = adapter.fromJson(json)

        assertNotNull(dto)
        assertEquals("BTCUSDT", dto?.symbol)
        assertEquals("28540.125", dto?.openInterest)
    }

    @Test
    fun testFuturesOrderBookParsing() {
        val json = """
            {
                "lastUpdateId": 1027024,
                "E": 1725266400123,
                "T": 1725266400120,
                "bids": [
                    ["109420.00", "4.500"],
                    ["109419.50", "2.120"]
                ],
                "asks": [
                    ["109420.50", "3.200"],
                    ["109421.00", "5.800"]
                ]
            }
        """.trimIndent()

        val adapter = moshi.adapter(FuturesOrderBookDto::class.java)
        val dto = adapter.fromJson(json)

        assertNotNull(dto)
        assertEquals(1027024L, dto?.lastUpdateId)
        assertEquals(2, dto?.bids?.size)
        assertEquals("109420.00", dto?.bids?.get(0)?.get(0))
        assertEquals(2, dto?.asks?.size)
        assertEquals("109420.50", dto?.asks?.get(0)?.get(0))
    }

    @Test
    fun testRetrofitClientConfiguration() {
        val service = CryptoApiClient.futuresApiService
        assertNotNull(service)
        assertNotNull(CryptoApiClient.okHttpClient)
        assertNotNull(CryptoApiClient.retrofit)
    }
}
