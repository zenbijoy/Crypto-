package com.example.ui.theme

import androidx.compose.ui.graphics.Color

// Modern Derivatives Terminal Design Tokens (Matching user screenshots)
// Light Palette (Default in screenshots)
val LightBackground = Color(0xFFF8F9FA)
val LightSurface = Color(0xFFFFFFFF)
val LightSurfaceRaised = Color(0xFFF1F3F5)
val LightBorder = Color(0xFFE9ECEF)
val LightTextPrimary = Color(0xFF1A1D20)
val LightTextMuted = Color(0xFF6C757D)
val LightTextSecondary = Color(0xFF868E96)

// Dark Palette
val DarkBackground = Color(0xFF0F141C)
val DarkSurface = Color(0xFF181F2A)
val DarkSurfaceRaised = Color(0xFF222B38)
val DarkBorder = Color(0xFF2A3444)
val DarkTextPrimary = Color(0xFFF1F3F5)
val DarkTextMuted = Color(0xFF909BA9)
val DarkTextSecondary = Color(0xFF6C7684)

// Brand & Semantic Accents
val BrandBlue = Color(0xFF2F54EB)          // Primary royal blue brand accent
val BrandBlueLight = Color(0xFFE8EFFF)     // Soft blue background
val BrandPurpleAI = Color(0xFF6366F1)      // AI badge gradient start
val BrandPinkAI = Color(0xFF8B5CF6)        // AI badge gradient end
val BrandGold = Color(0xFFF59E0B)          // Warning / highlight
val BrandGoldLight = Color(0xFFFEF3C7)     // Warning / gold background
val SemanticPositive = Color(0xFF00C087)    // Bullish, profit, longs
val SemanticPositiveLight = Color(0xFFE6F9F3)
val SemanticNegative = Color(0xFFF6465D)    // Bearish, loss, shorts
val SemanticNegativeLight = Color(0xFFFEECEE)
val SemanticWarning = Color(0xFFF59E0B)
val SemanticWarningLight = Color(0xFFFEF3C7)
val WarningSurface = Color(0xFFFEF3C7)
val SemanticInfo = Color(0xFF3B82F6)

// Exchange Specific Accents
val BinanceYellow = Color(0xFFF0B90B)
val BybitPurple = Color(0xFF7C3AED)
val OkxOrange = Color(0xFFF97316)
val GateBlue = Color(0xFF22D3EE)
val CoinbaseBlue = Color(0xFF0052FF)

// Legacy aliases
val BackgroundDark = DarkBackground
val SurfaceDark = DarkSurface
val SurfaceRaised = DarkSurfaceRaised
val BorderColor = DarkBorder
val TextPrimary = LightTextPrimary
val TextMuted = LightTextMuted
val PositiveSurface = SemanticPositiveLight
val NegativeSurface = SemanticNegativeLight
val GoldSurface = BrandGoldLight
val InfoSurface = BrandBlueLight
val CardBorder = LightBorder

