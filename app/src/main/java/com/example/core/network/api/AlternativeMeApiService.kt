package com.example.core.network.api

import com.example.core.network.dto.AlternativeMeFngResponseDto
import retrofit2.Response
import retrofit2.http.GET
import retrofit2.http.Query

interface AlternativeMeApiService {
    @GET("fng/")
    suspend fun getFearAndGreed(
        @Query("limit") limit: Int = 30
    ): Response<AlternativeMeFngResponseDto>
}
