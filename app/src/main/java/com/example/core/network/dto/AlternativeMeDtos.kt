package com.example.core.network.dto

import com.squareup.moshi.Json
import com.squareup.moshi.JsonClass

@JsonClass(generateAdapter = true)
data class AlternativeMeFngResponseDto(
    @Json(name = "name") val name: String? = null,
    @Json(name = "data") val data: List<AlternativeMeFngItemDto>? = null
)

@JsonClass(generateAdapter = true)
data class AlternativeMeFngItemDto(
    @Json(name = "value") val value: String,
    @Json(name = "value_classification") val valueClassification: String,
    @Json(name = "timestamp") val timestamp: String? = null,
    @Json(name = "time_until_update") val timeUntilUpdate: String? = null
)
