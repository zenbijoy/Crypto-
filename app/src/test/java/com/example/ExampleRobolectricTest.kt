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
    assertEquals("SIGN_IN", signInRoute.name)
    assertEquals("SIGN_UP", signUpRoute.name)
  }
}
