package com.example

import android.content.Context
import androidx.test.core.app.ApplicationProvider
import org.junit.Assert.assertEquals
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [36])
class ExampleRobolectricTest {

  @Test
  fun `read string from context`() {
    val context = ApplicationProvider.getApplicationContext<Context>()
    val appName = context.getString(R.string.app_name)
    assertEquals("CryptoScope AI", appName)
  }

  @Test
  fun `verify screen routes include auth destinations`() {
    val signInRoute = com.example.ui.viewmodel.ScreenRoute.SIGN_IN
    val signUpRoute = com.example.ui.viewmodel.ScreenRoute.SIGN_UP
    val watchlistRoute = com.example.ui.viewmodel.ScreenRoute.WATCHLIST
    assertEquals("SIGN_IN", signInRoute.name)
    assertEquals("SIGN_UP", signUpRoute.name)
    assertEquals("WATCHLIST", watchlistRoute.name)
  }

  @Test
  fun `verify language localization and translation mappings`() {
    val enTagline = com.example.ui.util.AppLocalization.tr("tagline", "English")
    val esTagline = com.example.ui.util.AppLocalization.tr("tagline", "Español")
    val jaTagline = com.example.ui.util.AppLocalization.tr("tagline", "日本語")

    assertEquals("Predict. Analyze. Trade Smarter.", enTagline)
    assertEquals("Predice. Analiza. Opera con Inteligencia.", esTagline)
    assertEquals("予測・分析・スマートな取引。", jaTagline)

    val supported = com.example.ui.util.AppLocalization.supportedLanguages
    org.junit.Assert.assertTrue(supported.size >= 7)
    org.junit.Assert.assertTrue(supported.any { it.code == "en" })
    org.junit.Assert.assertTrue(supported.any { it.code == "es" })
    org.junit.Assert.assertTrue(supported.any { it.code == "ja" })
  }

  @Test
  fun `verify viewmodel language state updating`() {
    val application = ApplicationProvider.getApplicationContext<android.app.Application>()
    val vm = com.example.ui.viewmodel.CryptoScopeViewModel(application)
    assertEquals("English", vm.uiState.value.selectedLanguage)

    vm.setLanguage("Español")
    assertEquals("Español", vm.uiState.value.selectedLanguage)

    vm.setLanguage("日本語")
    assertEquals("日本語", vm.uiState.value.selectedLanguage)
  }
}
