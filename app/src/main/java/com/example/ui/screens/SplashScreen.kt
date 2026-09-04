package com.example.ui.screens

import androidx.compose.animation.core.*
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.layout.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.painterResource
import com.example.R
import com.example.ui.viewmodel.CryptoScopeViewModel
import com.example.ui.viewmodel.ScreenRoute
import kotlinx.coroutines.delay

@Composable
fun SplashScreen(viewModel: CryptoScopeViewModel) {
    var isVisible by remember { mutableStateOf(false) }

    val alphaAnim by animateFloatAsState(
        targetValue = if (isVisible) 1f else 0f,
        animationSpec = tween(durationMillis = 600, easing = FastOutSlowInEasing),
        label = "splash_alpha"
    )

    LaunchedEffect(Unit) {
        isVisible = true
        delay(2200)
        viewModel.navigateTo(ScreenRoute.ONBOARDING)
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFFF8FAFC))
            .clickable(
                interactionSource = remember { MutableInteractionSource() },
                indication = null
            ) {
                viewModel.navigateTo(ScreenRoute.ONBOARDING)
            }
            .testTag("splash_screen"),
        contentAlignment = Alignment.Center
    ) {
        Image(
            painter = painterResource(id = R.drawable.splash_full),
            contentDescription = "CryptoScope AI Splash Screen",
            modifier = Modifier
                .fillMaxSize()
                .alpha(alphaAnim),
            contentScale = ContentScale.Crop
        )
    }
}

