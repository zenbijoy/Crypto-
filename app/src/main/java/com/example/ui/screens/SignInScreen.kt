package com.example.ui.screens

import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.KeyboardArrowDown
import androidx.compose.material.icons.outlined.Email
import androidx.compose.material.icons.outlined.Lock
import androidx.compose.material.icons.outlined.Person
import androidx.compose.material.icons.outlined.Visibility
import androidx.compose.material.icons.outlined.VisibilityOff
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.focus.onFocusChanged
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.*
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.SpanStyle
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.buildAnnotatedString
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.withStyle
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.R
import com.example.ui.util.AppLocalization
import com.example.ui.viewmodel.CryptoScopeViewModel
import com.example.ui.viewmodel.ScreenRoute

@Composable
fun SignInScreen(
    viewModel: CryptoScopeViewModel,
    initialIsSignUp: Boolean = false
) {
    var isSignUp by remember { mutableStateOf(initialIsSignUp) }
    val uiState by viewModel.uiState.collectAsState()
    val selectedLanguage = uiState.selectedLanguage
    var showLanguageMenu by remember { mutableStateOf(false) }

    // Form states
    var fullName by remember { mutableStateOf("") }
    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var confirmPassword by remember { mutableStateOf("") }

    var passwordVisible by remember { mutableStateOf(false) }
    var confirmPasswordVisible by remember { mutableStateOf(false) }
    var termsAccepted by remember { mutableStateOf(true) }

    var errorMessage by remember { mutableStateOf<String?>(null) }
    var showTermsDialog by remember { mutableStateOf(false) }
    var showForgotPasswordDialog by remember { mutableStateOf(false) }
    var forgotEmailInput by remember { mutableStateOf("") }
    var forgotSentMessage by remember { mutableStateOf<String?>(null) }

    val languages = listOf("English", "Español", "Français", "Deutsch", "日本語", "한국어", "中文")

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.White)
            .testTag("signin_screen")
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(bottom = 32.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            // Top Bar: Back Arrow & Language Selector
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 12.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                IconButton(
                    onClick = {
                        if (!viewModel.navigateBack()) {
                            viewModel.navigateTo(ScreenRoute.ONBOARDING)
                        }
                    },
                    modifier = Modifier.testTag("auth_back_button")
                ) {
                    Icon(
                        imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                        contentDescription = "Back",
                        tint = Color(0xFF0F172A),
                        modifier = Modifier.size(22.dp)
                    )
                }

                // Language Selector
                Box {
                    Row(
                        modifier = Modifier
                            .testTag("language_changer_button")
                            .clickable(
                                interactionSource = remember { MutableInteractionSource() },
                                indication = null
                            ) { showLanguageMenu = true }
                            .padding(horizontal = 8.dp, vertical = 6.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        val currentOpt = AppLocalization.supportedLanguages.firstOrNull {
                            it.displayName.equals(selectedLanguage, ignoreCase = true) ||
                            it.nativeName.equals(selectedLanguage, ignoreCase = true)
                        }
                        if (currentOpt != null) {
                            Text(text = currentOpt.flag, fontSize = 14.sp)
                            Spacer(modifier = Modifier.width(4.dp))
                        }
                        Text(
                            text = selectedLanguage,
                            fontSize = 14.sp,
                            fontWeight = FontWeight.Medium,
                            color = Color(0xFF334155)
                        )
                        Spacer(modifier = Modifier.width(4.dp))
                        Icon(
                            imageVector = Icons.Default.KeyboardArrowDown,
                            contentDescription = "Select Language",
                            tint = Color(0xFF334155),
                            modifier = Modifier.size(18.dp)
                        )
                    }

                    DropdownMenu(
                        expanded = showLanguageMenu,
                        onDismissRequest = { showLanguageMenu = false },
                        modifier = Modifier.background(Color.White)
                    ) {
                        AppLocalization.supportedLanguages.forEach { lang ->
                            val isSelected = lang.displayName.equals(selectedLanguage, ignoreCase = true) ||
                                    lang.nativeName.equals(selectedLanguage, ignoreCase = true)
                            DropdownMenuItem(
                                text = {
                                    Row(verticalAlignment = Alignment.CenterVertically) {
                                        Text(text = lang.flag, fontSize = 16.sp)
                                        Spacer(modifier = Modifier.width(8.dp))
                                        Text(
                                            text = "${lang.nativeName} (${lang.displayName})",
                                            fontSize = 14.sp,
                                            fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Normal,
                                            color = if (isSelected) Color(0xFF2563EB) else Color(0xFF0F172A)
                                        )
                                    }
                                },
                                onClick = {
                                    viewModel.setLanguage(lang.displayName)
                                    showLanguageMenu = false
                                },
                                modifier = Modifier.testTag("auth_lang_option_${lang.code}")
                            )
                        }
                    }
                }
            }

            Spacer(modifier = Modifier.height(8.dp))

            // Brand Header: Logo, Name & Tagline
            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
                modifier = Modifier.padding(horizontal = 24.dp)
            ) {
                Image(
                    painter = painterResource(id = R.drawable.ic_app_logo_trans),
                    contentDescription = "CryptoScope AI Logo",
                    modifier = Modifier
                        .size(76.dp)
                        .clip(CircleShape),
                    contentScale = ContentScale.Fit
                )

                Spacer(modifier = Modifier.height(12.dp))

                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(
                        text = "CryptoScope",
                        fontSize = 24.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFF0F172A),
                        letterSpacing = (-0.3).sp
                    )
                    Spacer(modifier = Modifier.width(5.dp))
                    Text(
                        text = "AI",
                        fontSize = 24.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFF7C3AED),
                        letterSpacing = (-0.3).sp
                    )
                }

                Spacer(modifier = Modifier.height(4.dp))

                Text(
                    text = AppLocalization.tr("tagline", selectedLanguage),
                    fontSize = 12.5.sp,
                    fontWeight = FontWeight.Medium,
                    color = Color(0xFF64748B),
                    letterSpacing = 0.2.sp
                )
            }

            Spacer(modifier = Modifier.height(28.dp))

            // Animated Switch between Sign Up ("Create your account") and Login ("Welcome back")
            AnimatedContent(
                targetState = isSignUp,
                transitionSpec = {
                    (fadeIn(animationSpec = tween(220)) + slideInHorizontally { if (targetState) it / 2 else -it / 2 })
                        .togetherWith(fadeOut(animationSpec = tween(220)))
                },
                label = "auth_mode_transition"
            ) { inSignUpMode ->
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 24.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    // Heading & Subtitle
                    Text(
                        text = if (inSignUpMode)
                            AppLocalization.tr("create_account_title", selectedLanguage)
                        else
                            AppLocalization.tr("welcome_back", selectedLanguage),
                        fontSize = 22.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFF0F172A),
                        textAlign = TextAlign.Center
                    )

                    Spacer(modifier = Modifier.height(6.dp))

                    Text(
                        text = if (inSignUpMode)
                            AppLocalization.tr("signup_subtitle", selectedLanguage)
                        else
                            AppLocalization.tr("signin_subtitle", selectedLanguage),
                        fontSize = 13.sp,
                        lineHeight = 18.sp,
                        fontWeight = FontWeight.Normal,
                        color = Color(0xFF64748B),
                        textAlign = TextAlign.Center
                    )

                    Spacer(modifier = Modifier.height(22.dp))

                    // Form Fields
                    if (inSignUpMode) {
                        // Full Name
                        AuthInputField(
                            value = fullName,
                            onValueChange = { fullName = it; errorMessage = null },
                            placeholder = AppLocalization.tr("full_name", selectedLanguage),
                            leadingIcon = Icons.Outlined.Person,
                            testTag = "full_name_input"
                        )
                        Spacer(modifier = Modifier.height(14.dp))
                    }

                    // Email Address
                    AuthInputField(
                        value = email,
                        onValueChange = { email = it; errorMessage = null },
                        placeholder = AppLocalization.tr("email_address", selectedLanguage),
                        leadingIcon = Icons.Outlined.Email,
                        keyboardType = KeyboardType.Email,
                        testTag = "email_input"
                    )

                    Spacer(modifier = Modifier.height(14.dp))

                    // Password
                    AuthInputField(
                        value = password,
                        onValueChange = { password = it; errorMessage = null },
                        placeholder = AppLocalization.tr("password", selectedLanguage),
                        leadingIcon = Icons.Outlined.Lock,
                        isPassword = true,
                        isPasswordVisible = passwordVisible,
                        onTogglePasswordVisibility = { passwordVisible = !passwordVisible },
                        keyboardType = KeyboardType.Password,
                        testTag = "password_input"
                    )

                    if (inSignUpMode) {
                        Spacer(modifier = Modifier.height(14.dp))

                        // Confirm Password
                        AuthInputField(
                            value = confirmPassword,
                            onValueChange = { confirmPassword = it; errorMessage = null },
                            placeholder = AppLocalization.tr("confirm_password", selectedLanguage),
                            leadingIcon = Icons.Outlined.Lock,
                            isPassword = true,
                            isPasswordVisible = confirmPasswordVisible,
                            onTogglePasswordVisibility = { confirmPasswordVisible = !confirmPasswordVisible },
                            keyboardType = KeyboardType.Password,
                            testTag = "confirm_password_input"
                        )

                        Spacer(modifier = Modifier.height(16.dp))

                        // Terms of Service & Privacy Policy Checkbox
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(vertical = 2.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Box(
                                modifier = Modifier
                                    .size(20.dp)
                                    .clip(RoundedCornerShape(5.dp))
                                    .background(if (termsAccepted) Color(0xFF2563EB) else Color.White)
                                    .border(
                                        width = if (termsAccepted) 0.dp else 1.5.dp,
                                        color = if (termsAccepted) Color.Transparent else Color(0xFFCBD5E1),
                                        shape = RoundedCornerShape(5.dp)
                                    )
                                    .clickable { termsAccepted = !termsAccepted }
                                    .testTag("terms_checkbox"),
                                contentAlignment = Alignment.Center
                            ) {
                                if (termsAccepted) {
                                    Icon(
                                        imageVector = Icons.Default.Check,
                                        contentDescription = "Checked",
                                        tint = Color.White,
                                        modifier = Modifier.size(14.dp)
                                    )
                                }
                            }

                            Spacer(modifier = Modifier.width(10.dp))

                            Text(
                                text = buildAnnotatedString {
                                    append("I agree to the ")
                                    withStyle(SpanStyle(color = Color(0xFF2563EB), fontWeight = FontWeight.Medium)) {
                                        append("Terms of Service")
                                    }
                                    append(" and\n")
                                    withStyle(SpanStyle(color = Color(0xFF2563EB), fontWeight = FontWeight.Medium)) {
                                        append("Privacy Policy")
                                    }
                                },
                                fontSize = 12.5.sp,
                                lineHeight = 17.sp,
                                color = Color(0xFF64748B),
                                modifier = Modifier.clickable { showTermsDialog = true }
                            )
                        }
                    } else {
                        // Forgot Password Link (Only in Log In mode)
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(top = 10.dp, bottom = 4.dp),
                            horizontalArrangement = Arrangement.End
                        ) {
                            Text(
                                text = AppLocalization.tr("forgot_password", selectedLanguage),
                                fontSize = 13.sp,
                                fontWeight = FontWeight.SemiBold,
                                color = Color(0xFF2563EB),
                                modifier = Modifier
                                    .clickable {
                                        forgotEmailInput = email
                                        forgotSentMessage = null
                                        showForgotPasswordDialog = true
                                    }
                                    .testTag("forgot_password_link")
                            )
                        }
                    }

                    // Error Banner if validation fails
                    if (errorMessage != null) {
                        Spacer(modifier = Modifier.height(10.dp))
                        Text(
                            text = errorMessage!!,
                            fontSize = 12.sp,
                            color = Color(0xFFEF4444),
                            fontWeight = FontWeight.Medium,
                            textAlign = TextAlign.Center,
                            modifier = Modifier.fillMaxWidth()
                        )
                    }

                    Spacer(modifier = Modifier.height(20.dp))

                    // Primary Gradient CTA Button ("Create Account" / "Log In")
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(52.dp)
                            .shadow(
                                elevation = 6.dp,
                                shape = RoundedCornerShape(14.dp),
                                spotColor = Color(0xFF7C3AED).copy(alpha = 0.35f),
                                ambientColor = Color(0xFF2563EB).copy(alpha = 0.25f)
                            )
                            .clip(RoundedCornerShape(14.dp))
                            .background(
                                Brush.horizontalGradient(
                                    listOf(
                                        Color(0xFF3B82F6),
                                        Color(0xFF6366F1),
                                        Color(0xFF8B5CF6),
                                        Color(0xFF9333EA)
                                    )
                                )
                            )
                            .clickable {
                                if (inSignUpMode) {
                                    if (email.isBlank() || password.isBlank()) {
                                        errorMessage = "Please fill in all required fields."
                                    } else if (password != confirmPassword) {
                                        errorMessage = "Passwords do not match."
                                    } else if (!termsAccepted) {
                                        errorMessage = "Please accept the Terms & Privacy Policy."
                                    } else {
                                        viewModel.signInSuccess(email)
                                    }
                                } else {
                                    if (email.isBlank() || password.isBlank()) {
                                        // Provide a fast default for testing convenience if user just presses Log In
                                        viewModel.signInSuccess(if (email.isNotBlank()) email else "trader@cryptoscope.ai")
                                    } else {
                                        viewModel.signInSuccess(email)
                                    }
                                }
                            }
                            .testTag(if (inSignUpMode) "create_account_button" else "sign_in_button"),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            text = if (inSignUpMode)
                                AppLocalization.tr("create_account", selectedLanguage)
                            else
                                AppLocalization.tr("log_in", selectedLanguage),
                            fontSize = 15.sp,
                            fontWeight = FontWeight.SemiBold,
                            color = Color.White,
                            letterSpacing = 0.3.sp
                        )
                    }

                    Spacer(modifier = Modifier.height(22.dp))

                    // Divider with "or continue with"
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        HorizontalDivider(
                            modifier = Modifier.weight(1f),
                            thickness = 1.dp,
                            color = Color(0xFFE2E8F0)
                        )
                        Text(
                            text = AppLocalization.tr("or_continue_with", selectedLanguage),
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Normal,
                            color = Color(0xFF94A3B8),
                            modifier = Modifier.padding(horizontal = 12.dp)
                        )
                        HorizontalDivider(
                            modifier = Modifier.weight(1f),
                            thickness = 1.dp,
                            color = Color(0xFFE2E8F0)
                        )
                    }

                    Spacer(modifier = Modifier.height(18.dp))

                    // Social Auth Buttons (Google, Apple, Telegram)
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        SocialLoginCard(
                            iconRes = R.drawable.ic_google,
                            contentDescription = "Google",
                            testTag = "google_signin_button",
                            onClick = { viewModel.signInSuccess("google.trader@cryptoscope.ai") }
                        )

                        SocialLoginCard(
                            iconRes = R.drawable.ic_apple,
                            contentDescription = "Apple",
                            testTag = "apple_signin_button",
                            onClick = { viewModel.signInSuccess("apple.trader@cryptoscope.ai") }
                        )

                        SocialLoginCard(
                            iconRes = R.drawable.ic_telegram,
                            contentDescription = "Telegram",
                            testTag = "telegram_signin_button",
                            onClick = { viewModel.signInSuccess("telegram.trader@cryptoscope.ai") }
                        )
                    }

                    Spacer(modifier = Modifier.height(24.dp))

                    // Switch Mode Footer
                    Row(
                        horizontalArrangement = Arrangement.Center,
                        verticalAlignment = Alignment.CenterVertically,
                        modifier = Modifier.padding(vertical = 4.dp)
                    ) {
                        Text(
                            text = if (inSignUpMode)
                                AppLocalization.tr("already_have_account", selectedLanguage)
                            else
                                AppLocalization.tr("dont_have_account", selectedLanguage),
                            fontSize = 13.5.sp,
                            color = Color(0xFF64748B)
                        )
                        Text(
                            text = if (inSignUpMode)
                                AppLocalization.tr("log_in", selectedLanguage)
                            else
                                AppLocalization.tr("sign_up", selectedLanguage),
                            fontSize = 13.5.sp,
                            fontWeight = FontWeight.Bold,
                            color = Color(0xFF2563EB),
                            modifier = Modifier
                                .clickable {
                                    errorMessage = null
                                    isSignUp = !isSignUp
                                }
                                .padding(start = 2.dp)
                                .testTag("toggle_auth_mode_button")
                        )
                    }

                    Spacer(modifier = Modifier.height(16.dp))

                    // Bottom Illustration Graphic matching the mockup
                    if (inSignUpMode) {
                        // Sign Up delicate wavy contours
                        SignUpWaveVisual(
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(120.dp)
                        )
                    } else {
                        // Log In 3D Crypto Dashboard Perspective Showcase
                        LoginShowcaseVisual(
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(220.dp)
                        )
                    }
                }
            }
        }
    }

    // Terms Dialog
    if (showTermsDialog) {
        AlertDialog(
            onDismissRequest = { showTermsDialog = false },
            title = {
                Text(
                    text = "Terms & Privacy Policy",
                    fontWeight = FontWeight.Bold,
                    fontSize = 18.sp,
                    color = Color(0xFF0F172A)
                )
            },
            text = {
                Text(
                    text = "By using CryptoScope AI, you acknowledge that all AI predictions, probabilistic bounds (P10-P90), and microstructure analysis are for market intelligence and informational purposes only and do not constitute financial advice.\n\nYour account credentials and sensitive preferences are encrypted locally on device.",
                    fontSize = 13.sp,
                    lineHeight = 18.sp,
                    color = Color(0xFF475569)
                )
            },
            confirmButton = {
                TextButton(onClick = { showTermsDialog = false }) {
                    Text("I Understand", color = Color(0xFF2563EB), fontWeight = FontWeight.Bold)
                }
            },
            containerColor = Color.White
        )
    }

    // Forgot Password Dialog
    if (showForgotPasswordDialog) {
        AlertDialog(
            onDismissRequest = { showForgotPasswordDialog = false },
            title = {
                Text(
                    text = "Reset Password",
                    fontWeight = FontWeight.Bold,
                    fontSize = 18.sp,
                    color = Color(0xFF0F172A)
                )
            },
            text = {
                Column {
                    Text(
                        text = "Enter your email address to receive password reset instructions.",
                        fontSize = 13.sp,
                        color = Color(0xFF64748B)
                    )
                    Spacer(modifier = Modifier.height(14.dp))
                    AuthInputField(
                        value = forgotEmailInput,
                        onValueChange = { forgotEmailInput = it },
                        placeholder = "Email Address",
                        leadingIcon = Icons.Outlined.Email,
                        keyboardType = KeyboardType.Email
                    )
                    if (forgotSentMessage != null) {
                        Spacer(modifier = Modifier.height(10.dp))
                        Text(
                            text = forgotSentMessage!!,
                            fontSize = 12.sp,
                            color = Color(0xFF10B981),
                            fontWeight = FontWeight.Medium
                        )
                    }
                }
            },
            confirmButton = {
                TextButton(
                    onClick = {
                        if (forgotEmailInput.isNotBlank()) {
                            forgotSentMessage = "Reset link sent to $forgotEmailInput"
                        }
                    }
                ) {
                    Text("Send Link", color = Color(0xFF2563EB), fontWeight = FontWeight.Bold)
                }
            },
            dismissButton = {
                TextButton(onClick = { showForgotPasswordDialog = false }) {
                    Text("Close", color = Color(0xFF64748B))
                }
            },
            containerColor = Color.White
        )
    }
}

/**
 * Pixel-perfect Auth Input Field with rounded border and leading/trailing icons
 */
@Composable
private fun AuthInputField(
    value: String,
    onValueChange: (String) -> Unit,
    placeholder: String,
    leadingIcon: ImageVector,
    isPassword: Boolean = false,
    isPasswordVisible: Boolean = false,
    onTogglePasswordVisibility: (() -> Unit)? = null,
    keyboardType: KeyboardType = KeyboardType.Text,
    testTag: String = ""
) {
    var isFocused by remember { mutableStateOf(false) }

    Row(
        modifier = Modifier
            .fillMaxWidth()
            .height(52.dp)
            .clip(RoundedCornerShape(12.dp))
            .background(Color.White)
            .border(
                width = if (isFocused) 1.5.dp else 1.dp,
                color = if (isFocused) Color(0xFF3B82F6) else Color(0xFFE2E8F0),
                shape = RoundedCornerShape(12.dp)
            )
            .padding(horizontal = 16.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(
            imageVector = leadingIcon,
            contentDescription = null,
            tint = if (isFocused) Color(0xFF3B82F6) else Color(0xFF94A3B8),
            modifier = Modifier.size(20.dp)
        )

        Spacer(modifier = Modifier.width(12.dp))

        Box(
            modifier = Modifier
                .weight(1f)
                .fillMaxHeight(),
            contentAlignment = Alignment.CenterStart
        ) {
            if (value.isEmpty()) {
                Text(
                    text = placeholder,
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Normal,
                    color = Color(0xFF94A3B8)
                )
            }
            BasicTextField(
                value = value,
                onValueChange = onValueChange,
                modifier = Modifier
                    .fillMaxWidth()
                    .onFocusChanged { isFocused = it.isFocused }
                    .then(if (testTag.isNotEmpty()) Modifier.testTag(testTag) else Modifier),
                singleLine = true,
                textStyle = TextStyle(
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Normal,
                    color = Color(0xFF0F172A)
                ),
                keyboardOptions = KeyboardOptions(keyboardType = keyboardType),
                visualTransformation = if (isPassword && !isPasswordVisible) PasswordVisualTransformation() else VisualTransformation.None,
                cursorBrush = SolidColor(Color(0xFF3B82F6))
            )
        }

        if (isPassword && onTogglePasswordVisibility != null) {
            IconButton(
                onClick = onTogglePasswordVisibility,
                modifier = Modifier.size(28.dp)
            ) {
                Icon(
                    imageVector = if (isPasswordVisible) Icons.Outlined.Visibility else Icons.Outlined.VisibilityOff,
                    contentDescription = if (isPasswordVisible) "Hide password" else "Show password",
                    tint = Color(0xFF94A3B8),
                    modifier = Modifier.size(20.dp)
                )
            }
        }
    }
}

/**
 * Social Login card with white surface, rounded border and centered icon
 */
@Composable
private fun SocialLoginCard(
    iconRes: Int,
    contentDescription: String,
    testTag: String,
    onClick: () -> Unit
) {
    Box(
        modifier = Modifier
            .width(96.dp)
            .height(52.dp)
            .shadow(
                elevation = 2.dp,
                shape = RoundedCornerShape(14.dp),
                spotColor = Color(0x14000000)
            )
            .clip(RoundedCornerShape(14.dp))
            .background(Color.White)
            .border(1.dp, Color(0xFFE2E8F0), RoundedCornerShape(14.dp))
            .clickable(onClick = onClick)
            .testTag(testTag),
        contentAlignment = Alignment.Center
    ) {
        Icon(
            painter = painterResource(id = iconRes),
            contentDescription = contentDescription,
            tint = Color.Unspecified,
            modifier = Modifier.size(22.dp)
        )
    }
}

/**
 * Subtle wave contour graphic at the bottom of the Sign Up screen
 */
@Composable
private fun SignUpWaveVisual(modifier: Modifier = Modifier) {
    Canvas(modifier = modifier) {
        val w = size.width
        val h = size.height

        // Soft gradient waves
        val waveColor1 = Color(0xFF3B82F6).copy(alpha = 0.18f)
        val waveColor2 = Color(0xFF8B5CF6).copy(alpha = 0.22f)
        val waveColor3 = Color(0xFF00D2FF).copy(alpha = 0.15f)

        fun drawWave(yOffset: Float, amplitude: Float, color: Color, strokeWidth: Float) {
            val path = Path().apply {
                moveTo(0f, yOffset)
                cubicTo(
                    w * 0.25f, yOffset - amplitude,
                    w * 0.45f, yOffset + amplitude,
                    w * 0.70f, yOffset - amplitude * 0.6f
                )
                cubicTo(
                    w * 0.85f, yOffset - amplitude * 1.2f,
                    w * 0.95f, yOffset + amplitude * 0.4f,
                    w, yOffset
                )
            }
            drawPath(
                path = path,
                color = color,
                style = Stroke(width = strokeWidth, cap = StrokeCap.Round)
            )
        }

        drawWave(h * 0.45f, 24f, waveColor1, 1.6.dp.toPx())
        drawWave(h * 0.58f, 20f, waveColor2, 1.4.dp.toPx())
        drawWave(h * 0.70f, 28f, waveColor3, 1.2.dp.toPx())
        drawWave(h * 0.82f, 18f, waveColor1.copy(alpha = 0.12f), 1.0.dp.toPx())
    }
}

/**
 * 3D Crypto Dashboard Showcase Visual with floating perspective phone,
 * candlestick chart, Bitcoin coin, Ethereum crystal, Tether coin, and floating metric pills
 */
@Composable
private fun LoginShowcaseVisual(modifier: Modifier = Modifier) {
    Box(
        modifier = modifier,
        contentAlignment = Alignment.Center
    ) {
        // Background soft gradient ambient glows
        Canvas(modifier = Modifier.fillMaxSize()) {
            drawCircle(
                brush = Brush.radialGradient(
                    colors = listOf(Color(0xFFE0F2FE).copy(alpha = 0.8f), Color.Transparent),
                    center = Offset(size.width * 0.25f, size.height * 0.6f),
                    radius = size.width * 0.35f
                )
            )
            drawCircle(
                brush = Brush.radialGradient(
                    colors = listOf(Color(0xFFF3E8FF).copy(alpha = 0.7f), Color.Transparent),
                    center = Offset(size.width * 0.8f, size.height * 0.5f),
                    radius = size.width * 0.4f
                )
            )
        }

        // Center Phone Mockup Card
        Box(
            modifier = Modifier
                .width(190.dp)
                .height(180.dp)
                .shadow(
                    elevation = 12.dp,
                    shape = RoundedCornerShape(20.dp),
                    spotColor = Color(0x223B82F6),
                    ambientColor = Color(0x14000000)
                )
                .clip(RoundedCornerShape(20.dp))
                .background(Color.White)
                .border(1.dp, Color(0xFFF1F5F9), RoundedCornerShape(20.dp))
                .padding(12.dp)
        ) {
            Column(modifier = Modifier.fillMaxSize()) {
                // Header
                Text(
                    text = "BTCUSDT",
                    fontSize = 10.sp,
                    fontWeight = FontWeight.SemiBold,
                    color = Color(0xFF64748B)
                )
                Spacer(modifier = Modifier.height(2.dp))
                Row(
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "67,318.45",
                        fontSize = 14.sp,
                        fontWeight = FontWeight.ExtraBold,
                        color = Color(0xFF0F172A)
                    )
                    Spacer(modifier = Modifier.width(6.dp))
                    Box(
                        modifier = Modifier
                            .clip(RoundedCornerShape(4.dp))
                            .background(Color(0xFFECFDF5))
                            .padding(horizontal = 4.dp, vertical = 2.dp)
                    ) {
                        Text(
                            text = "+2.35%",
                            fontSize = 9.sp,
                            fontWeight = FontWeight.Bold,
                            color = Color(0xFF10B981)
                        )
                    }
                }

                Spacer(modifier = Modifier.height(8.dp))

                // Realistic Candlestick Area Graphic
                Canvas(
                    modifier = Modifier
                        .fillMaxWidth()
                        .weight(1f)
                ) {
                    val w = size.width
                    val h = size.height

                    // Gradient area
                    val areaPath = Path().apply {
                        moveTo(0f, h)
                        lineTo(0f, h * 0.75f)
                        cubicTo(w * 0.25f, h * 0.8f, w * 0.45f, h * 0.5f, w * 0.7f, h * 0.4f)
                        cubicTo(w * 0.85f, h * 0.35f, w * 0.95f, h * 0.25f, w, h * 0.2f)
                        lineTo(w, h)
                        close()
                    }
                    drawPath(
                        path = areaPath,
                        brush = Brush.verticalGradient(
                            listOf(Color(0xFF38BDF8).copy(alpha = 0.3f), Color.Transparent)
                        )
                    )

                    // Trend line
                    val linePath = Path().apply {
                        moveTo(0f, h * 0.75f)
                        cubicTo(w * 0.25f, h * 0.8f, w * 0.45f, h * 0.5f, w * 0.7f, h * 0.4f)
                        cubicTo(w * 0.85f, h * 0.35f, w * 0.95f, h * 0.25f, w, h * 0.2f)
                    }
                    drawPath(
                        path = linePath,
                        color = Color(0xFF0284C7),
                        style = Stroke(width = 2.dp.toPx(), cap = StrokeCap.Round)
                    )

                    // Candlestick bars
                    val candleData = listOf(
                        Triple(0.12f, 0.72f, 0.60f),
                        Triple(0.24f, 0.65f, 0.52f),
                        Triple(0.36f, 0.58f, 0.66f),
                        Triple(0.48f, 0.52f, 0.44f),
                        Triple(0.60f, 0.46f, 0.36f),
                        Triple(0.72f, 0.40f, 0.48f),
                        Triple(0.84f, 0.34f, 0.26f),
                        Triple(0.94f, 0.25f, 0.18f)
                    )

                    candleData.forEach { (xRel, openRel, closeRel) ->
                        val cx = w * xRel
                        val topY = h * minOf(openRel, closeRel)
                        val botY = h * maxOf(openRel, closeRel)
                        val isGreen = closeRel < openRel
                        val color = if (isGreen) Color(0xFF0284C7) else Color(0xFF9333EA)

                        // Wick
                        drawLine(
                            color = color.copy(alpha = 0.6f),
                            start = Offset(cx, topY - 5f),
                            end = Offset(cx, botY + 5f),
                            strokeWidth = 1.2.dp.toPx()
                        )
                        // Body
                        drawRoundRect(
                            color = color,
                            topLeft = Offset(cx - 3.5.dp.toPx(), topY),
                            size = Size(7.dp.toPx(), maxOf(6f, botY - topY)),
                            cornerRadius = CornerRadius(1.5.dp.toPx(), 1.5.dp.toPx())
                        )
                    }
                }
            }
        }

        // Floating Bitcoin Token (Left)
        Box(
            modifier = Modifier
                .align(Alignment.CenterStart)
                .offset(x = 16.dp, y = (-15).dp)
                .size(42.dp)
                .shadow(elevation = 6.dp, shape = CircleShape, spotColor = Color(0x33F7931A))
                .clip(CircleShape)
                .background(
                    Brush.radialGradient(
                        listOf(Color(0xFFFFB74D), Color(0xFFF7931A))
                    )
                )
                .border(1.5.dp, Color.White, CircleShape),
            contentAlignment = Alignment.Center
        ) {
            Text(
                text = "₿",
                fontSize = 20.sp,
                fontWeight = FontWeight.Bold,
                color = Color.White
            )
        }

        // Floating Ethereum Crystal Token (Right)
        Box(
            modifier = Modifier
                .align(Alignment.CenterEnd)
                .offset(x = (-16).dp, y = (-30).dp)
                .size(42.dp)
                .shadow(elevation = 6.dp, shape = CircleShape, spotColor = Color(0x336366F1))
                .clip(CircleShape)
                .background(
                    Brush.radialGradient(
                        listOf(Color(0xFF818CF8), Color(0xFF4F46E5))
                    )
                )
                .border(1.5.dp, Color.White, CircleShape),
            contentAlignment = Alignment.Center
        ) {
            Canvas(modifier = Modifier.size(20.dp)) {
                val cx = size.width / 2f
                val cy = size.height / 2f
                // Faceted ETH diamond top
                val topPath = Path().apply {
                    moveTo(cx, 0f)
                    lineTo(size.width, cy)
                    lineTo(cx, cy * 1.35f)
                    lineTo(0f, cy)
                    close()
                }
                drawPath(topPath, Color.White)
                // Bottom facet
                val botPath = Path().apply {
                    moveTo(cx, size.height)
                    lineTo(size.width * 0.85f, cy * 1.45f)
                    lineTo(size.width * 0.15f, cy * 1.45f)
                    close()
                }
                drawPath(botPath, Color.White.copy(alpha = 0.85f))
            }
        }

        // Floating Tether Token (Bottom Right)
        Box(
            modifier = Modifier
                .align(Alignment.BottomEnd)
                .offset(x = (-22).dp, y = (-12).dp)
                .size(36.dp)
                .shadow(elevation = 4.dp, shape = CircleShape, spotColor = Color(0x3326A17B))
                .clip(CircleShape)
                .background(
                    Brush.radialGradient(
                        listOf(Color(0xFF34D399), Color(0xFF059669))
                    )
                )
                .border(1.2.dp, Color.White, CircleShape),
            contentAlignment = Alignment.Center
        ) {
            Text(
                text = "₮",
                fontSize = 17.sp,
                fontWeight = FontWeight.Bold,
                color = Color.White
            )
        }

        // Floating Glassmorphic Metric Card: Funding Rate (Bottom Left)
        Box(
            modifier = Modifier
                .align(Alignment.BottomStart)
                .offset(x = 10.dp, y = 6.dp)
                .shadow(
                    elevation = 6.dp,
                    shape = RoundedCornerShape(12.dp),
                    spotColor = Color(0x1A000000)
                )
                .clip(RoundedCornerShape(12.dp))
                .background(Color.White)
                .border(1.dp, Color(0xFFF1F5F9), RoundedCornerShape(12.dp))
                .padding(horizontal = 10.dp, vertical = 6.dp)
        ) {
            Column {
                Text(
                    text = "Funding Rate",
                    fontSize = 9.sp,
                    color = Color(0xFF64748B),
                    fontWeight = FontWeight.Medium
                )
                Text(
                    text = "0.0102%",
                    fontSize = 12.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color(0xFF0F172A)
                )
            }
        }

        // Floating Glassmorphic Metric Card: Open Interest (Bottom Right-Center)
        Box(
            modifier = Modifier
                .align(Alignment.BottomEnd)
                .offset(x = (-55).dp, y = 14.dp)
                .shadow(
                    elevation = 6.dp,
                    shape = RoundedCornerShape(12.dp),
                    spotColor = Color(0x1A000000)
                )
                .clip(RoundedCornerShape(12.dp))
                .background(Color.White)
                .border(1.dp, Color(0xFFF1F5F9), RoundedCornerShape(12.dp))
                .padding(horizontal = 10.dp, vertical = 6.dp)
        ) {
            Column {
                Text(
                    text = "Open Interest",
                    fontSize = 9.sp,
                    color = Color(0xFF64748B),
                    fontWeight = FontWeight.Medium
                )
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(
                        text = "$38.46B",
                        fontSize = 12.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFF0F172A)
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text(
                        text = "+3.25%",
                        fontSize = 9.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFF10B981)
                    )
                }
            }
        }
    }
}
