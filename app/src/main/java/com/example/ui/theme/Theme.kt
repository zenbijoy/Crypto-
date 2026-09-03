package com.example.ui.theme

import android.app.Activity
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat

private val CryptoScopeLightColorScheme = lightColorScheme(
    primary = BrandBlue,
    onPrimary = LightSurface,
    primaryContainer = BrandBlueLight,
    onPrimaryContainer = BrandBlue,
    secondary = BrandPurpleAI,
    onSecondary = LightSurface,
    secondaryContainer = BrandBlueLight,
    onSecondaryContainer = BrandBlue,
    tertiary = SemanticPositive,
    onTertiary = LightSurface,
    background = LightBackground,
    onBackground = LightTextPrimary,
    surface = LightSurface,
    onSurface = LightTextPrimary,
    surfaceVariant = LightSurfaceRaised,
    onSurfaceVariant = LightTextMuted,
    outline = LightBorder,
    error = SemanticNegative,
    onError = LightSurface
)

private val CryptoScopeDarkColorScheme = darkColorScheme(
    primary = BrandBlue,
    onPrimary = DarkTextPrimary,
    primaryContainer = DarkSurfaceRaised,
    onPrimaryContainer = BrandBlue,
    secondary = BrandPurpleAI,
    onSecondary = DarkTextPrimary,
    secondaryContainer = DarkSurfaceRaised,
    onSecondaryContainer = BrandPurpleAI,
    tertiary = SemanticPositive,
    onTertiary = DarkBackground,
    background = DarkBackground,
    onBackground = DarkTextPrimary,
    surface = DarkSurface,
    onSurface = DarkTextPrimary,
    surfaceVariant = DarkSurfaceRaised,
    onSurfaceVariant = DarkTextMuted,
    outline = DarkBorder,
    error = SemanticNegative,
    onError = DarkTextPrimary
)

@Composable
fun CryptoScopeTheme(
    darkTheme: Boolean = false, // Clean light terminal design matching user screenshots
    content: @Composable () -> Unit
) {
    val colorScheme = if (darkTheme) CryptoScopeDarkColorScheme else CryptoScopeLightColorScheme
    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as? Activity)?.window
            if (window != null) {
                window.statusBarColor = (if (darkTheme) DarkBackground else LightSurface).toArgb()
                window.navigationBarColor = (if (darkTheme) DarkSurface else LightSurface).toArgb()
                WindowCompat.getInsetsController(window, view).isAppearanceLightStatusBars = !darkTheme
                WindowCompat.getInsetsController(window, view).isAppearanceLightNavigationBars = !darkTheme
            }
        }
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content
    )
}

// Alias for compatibility
@Composable
fun MyApplicationTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    dynamicColor: Boolean = false,
    content: @Composable () -> Unit
) {
    CryptoScopeTheme(darkTheme = darkTheme, content = content)
}

