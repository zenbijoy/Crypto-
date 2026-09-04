package com.example.ui.screens

import android.widget.Toast
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.automirrored.filled.KeyboardArrowRight
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalClipboardManager
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.ui.theme.*
import com.example.ui.viewmodel.CryptoScopeViewModel
import com.example.ui.viewmodel.ScreenRoute

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun UserCenterScreen(viewModel: CryptoScopeViewModel) {
    val uiState by viewModel.uiState.collectAsState()
    val isDark = uiState.isDarkTheme
    val bgColor = if (isDark) DarkBackground else LightBackground
    val cardColor = if (isDark) DarkSurface else LightSurface
    val borderColor = if (isDark) DarkBorder else LightBorder
    val textColor = if (isDark) DarkTextPrimary else LightTextPrimary
    val textMutedColor = if (isDark) DarkTextMuted else LightTextMuted
    val clipboardManager = LocalClipboardManager.current
    val context = LocalContext.current

    var selectedTab by remember { mutableStateOf("General") }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Text(
                        text = "User Center",
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold,
                        color = textColor
                    )
                },
                actions = {
                    IconButton(onClick = { viewModel.navigateTo(ScreenRoute.NOTIFICATIONS) }) {
                        Icon(
                            imageVector = Icons.Default.Notifications,
                            contentDescription = "Notifications",
                            tint = textColor
                        )
                    }
                    IconButton(onClick = {
                        Toast.makeText(context, "Points & Rewards Hub", Toast.LENGTH_SHORT).show()
                    }) {
                        Icon(
                            imageVector = Icons.Default.CardGiftcard,
                            contentDescription = "Rewards",
                            tint = BrandBlue
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = cardColor)
            )
        },
        containerColor = bgColor
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .background(bgColor)
                .verticalScroll(rememberScrollState())
                .padding(16.dp)
                .testTag("user_center_screen"),
            verticalArrangement = Arrangement.spacedBy(14.dp)
        ) {
            // Profile Card
            Surface(
                shape = RoundedCornerShape(16.dp),
                color = cardColor,
                border = BorderStroke(1.dp, borderColor),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        // Avatar
                        Box(
                            modifier = Modifier
                                .size(56.dp)
                                .clip(CircleShape)
                                .background(BrandBlueLight),
                            contentAlignment = Alignment.Center
                        ) {
                            Text(
                                text = uiState.userProfile.nickname.take(2).uppercase(),
                                fontSize = 20.sp,
                                fontWeight = FontWeight.Bold,
                                color = BrandBlue
                            )
                        }

                        Spacer(modifier = Modifier.width(14.dp))

                        Column(modifier = Modifier.weight(1f)) {
                            Text(
                                text = uiState.userProfile.nickname,
                                fontSize = 16.sp,
                                fontWeight = FontWeight.Bold,
                                color = textColor
                            )
                            Spacer(modifier = Modifier.height(4.dp))
                            Row(
                                verticalAlignment = Alignment.CenterVertically,
                                modifier = Modifier.clickable {
                                    clipboardManager.setText(AnnotatedString(uiState.userProfile.uid))
                                    Toast.makeText(context, "UID Copied: ${uiState.userProfile.uid}", Toast.LENGTH_SHORT).show()
                                }
                            ) {
                                Text(
                                    text = "UID: ${uiState.userProfile.uid}",
                                    fontSize = 12.sp,
                                    color = textMutedColor
                                )
                                Spacer(modifier = Modifier.width(4.dp))
                                Icon(
                                    imageVector = Icons.Default.ContentCopy,
                                    contentDescription = "Copy UID",
                                    tint = textMutedColor,
                                    modifier = Modifier.size(12.dp)
                                )
                            }
                        }

                        // Edit Profile Button
                        OutlinedButton(
                            onClick = { viewModel.navigateTo(ScreenRoute.EDIT_PROFILE) },
                            shape = RoundedCornerShape(20.dp),
                            border = BorderStroke(1.dp, BrandBlue),
                            contentPadding = PaddingValues(horizontal = 12.dp, vertical = 4.dp),
                            modifier = Modifier.testTag("edit_profile_button")
                        ) {
                            Text(
                                text = "Edit Profile",
                                fontSize = 11.sp,
                                fontWeight = FontWeight.Bold,
                                color = BrandBlue
                            )
                        }
                    }

                    if (uiState.userProfile.bio.isNotBlank()) {
                        Spacer(modifier = Modifier.height(10.dp))
                        Text(
                            text = uiState.userProfile.bio,
                            fontSize = 12.sp,
                            color = textMutedColor
                        )
                    }
                }
            }

            // Membership Card
            Surface(
                shape = RoundedCornerShape(16.dp),
                color = cardColor,
                border = BorderStroke(1.dp, borderColor),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = "Membership: ${uiState.userProfile.membership}",
                            fontSize = 14.sp,
                            fontWeight = FontWeight.Bold,
                            color = textColor
                        )
                        Surface(
                            shape = RoundedCornerShape(6.dp),
                            color = BrandBlueLight
                        ) {
                            Text(
                                text = "${uiState.userProfile.points} PTS",
                                fontSize = 11.sp,
                                fontWeight = FontWeight.Bold,
                                color = BrandBlue,
                                modifier = Modifier.padding(horizontal = 8.dp, vertical = 3.dp)
                            )
                        }
                    }

                    Spacer(modifier = Modifier.height(10.dp))

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Column {
                            Text("Expires At", fontSize = 11.sp, color = textMutedColor)
                            Text(uiState.userProfile.membershipExpiry, fontSize = 12.sp, fontWeight = FontWeight.SemiBold, color = textColor)
                        }
                        Column {
                            Text("API Key", fontSize = 11.sp, color = textMutedColor)
                            Text(uiState.userProfile.apiKey, fontSize = 12.sp, fontWeight = FontWeight.SemiBold, color = textColor)
                        }
                        Column {
                            Text("Invite Code", fontSize = 11.sp, color = textMutedColor)
                            Text(uiState.userProfile.inviteCode, fontSize = 12.sp, fontWeight = FontWeight.SemiBold, color = BrandBlue)
                        }
                    }
                }
            }

            // Tabs (General, Account, VIP/Points, Invite)
            Surface(
                shape = RoundedCornerShape(12.dp),
                color = if (isDark) DarkSurfaceRaised else LightSurfaceRaised,
                modifier = Modifier.fillMaxWidth()
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(4.dp),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    listOf("General", "Account", "VIP/Points", "Invite").forEach { tab ->
                        val selected = selectedTab == tab
                        Surface(
                            shape = RoundedCornerShape(8.dp),
                            color = if (selected) cardColor else Color.Transparent,
                            modifier = Modifier
                                .weight(1f)
                                .clickable { selectedTab = tab }
                        ) {
                            Text(
                                text = tab,
                                fontSize = 12.sp,
                                fontWeight = if (selected) FontWeight.Bold else FontWeight.Normal,
                                color = if (selected) BrandBlue else textMutedColor,
                                modifier = Modifier
                                    .padding(vertical = 8.dp)
                                    .wrapContentWidth(Alignment.CenterHorizontally)
                            )
                        }
                    }
                }
            }

            // Settings List items
            Surface(
                shape = RoundedCornerShape(16.dp),
                color = cardColor,
                border = BorderStroke(1.dp, borderColor),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column {
                    // Floating Window
                    SettingsRow(
                        title = "Floating Window",
                        subtitle = "Fast widget on desktop",
                        onClick = { Toast.makeText(context, "Floating window enabled", Toast.LENGTH_SHORT).show() },
                        textColor = textColor,
                        borderColor = borderColor
                    )

                    // Appearance (Day/Night switch)
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(horizontal = 16.dp, vertical = 12.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column {
                            Text(text = "Appearance", fontSize = 14.sp, fontWeight = FontWeight.Medium, color = textColor)
                            Text(text = if (isDark) "Dark Mode" else "Light Mode", fontSize = 11.sp, color = textMutedColor)
                        }
                        Switch(
                            checked = isDark,
                            onCheckedChange = { viewModel.toggleDarkTheme() },
                            colors = SwitchDefaults.colors(
                                checkedThumbColor = Color.White,
                                checkedTrackColor = BrandBlue,
                                uncheckedThumbColor = Color.White,
                                uncheckedTrackColor = LightBorder
                            )
                        )
                    }
                    HorizontalDivider(color = borderColor, thickness = 0.5.dp)

                    // Color Preference
                    SettingsRow(
                        title = "Color Preference",
                        value = if (uiState.colorPreferenceGreenPositive) "Green+ Red-" else "Red+ Green-",
                        onClick = { viewModel.toggleColorPreference() },
                        textColor = textColor,
                        borderColor = borderColor
                    )

                    // Language
                    SettingsRow(
                        title = "Language",
                        value = "English",
                        onClick = { Toast.makeText(context, "Language: English", Toast.LENGTH_SHORT).show() },
                        textColor = textColor,
                        borderColor = borderColor
                    )

                    // Screenshot Sharing toggle
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(horizontal = 16.dp, vertical = 12.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column {
                            Text(text = "Screenshot sharing", fontSize = 14.sp, fontWeight = FontWeight.Medium, color = textColor)
                            Text(text = "Quick share sheet on capture", fontSize = 11.sp, color = textMutedColor)
                        }
                        Switch(
                            checked = uiState.screenshotSharingEnabled,
                            onCheckedChange = { viewModel.toggleScreenshotSharing() },
                            colors = SwitchDefaults.colors(
                                checkedThumbColor = Color.White,
                                checkedTrackColor = BrandBlue,
                                uncheckedThumbColor = Color.White,
                                uncheckedTrackColor = LightBorder
                            )
                        )
                    }
                    HorizontalDivider(color = borderColor, thickness = 0.5.dp)

                    // Share App
                    SettingsRow(
                        title = "Share App",
                        onClick = { Toast.makeText(context, "Sharing CryptoScope AI", Toast.LENGTH_SHORT).show() },
                        textColor = textColor,
                        borderColor = borderColor
                    )

                    // Contact Us
                    SettingsRow(
                        title = "Contact Us",
                        value = "support@cryptoscope.ai",
                        onClick = { Toast.makeText(context, "Email support@cryptoscope.ai", Toast.LENGTH_SHORT).show() },
                        textColor = textColor,
                        borderColor = borderColor
                    )

                    // Check for Update
                    SettingsRow(
                        title = "Check for update",
                        value = "GPlay AAB 3.9.9(39905)",
                        onClick = { Toast.makeText(context, "App is up to date (3.9.9)", Toast.LENGTH_SHORT).show() },
                        textColor = textColor,
                        borderColor = borderColor,
                        showDivider = true
                    )

                    // Switch Account / Log In
                    SettingsRow(
                        title = "Account Access",
                        value = "Sign In / Sign Up",
                        onClick = { viewModel.navigateTo(ScreenRoute.SIGN_IN) },
                        textColor = BrandBlue,
                        borderColor = borderColor,
                        showDivider = false
                    )
                }
            }

            Spacer(modifier = Modifier.height(20.dp))
        }
    }
}

@Composable
fun SettingsRow(
    title: String,
    subtitle: String? = null,
    value: String? = null,
    onClick: () -> Unit,
    textColor: Color,
    borderColor: Color,
    showDivider: Boolean = true
) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { onClick() }
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 16.dp, vertical = 14.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column {
                Text(text = title, fontSize = 14.sp, fontWeight = FontWeight.Medium, color = textColor)
                if (subtitle != null) {
                    Text(text = subtitle, fontSize = 11.sp, color = LightTextMuted)
                }
            }

            Row(verticalAlignment = Alignment.CenterVertically) {
                if (value != null) {
                    Text(text = value, fontSize = 12.sp, color = LightTextMuted)
                    Spacer(modifier = Modifier.width(4.dp))
                }
                Icon(
                    imageVector = Icons.AutoMirrored.Filled.KeyboardArrowRight,
                    contentDescription = null,
                    tint = LightTextMuted,
                    modifier = Modifier.size(18.dp)
                )
            }
        }
        if (showDivider) {
            HorizontalDivider(color = borderColor, thickness = 0.5.dp)
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun EditProfileScreen(viewModel: CryptoScopeViewModel) {
    val uiState by viewModel.uiState.collectAsState()
    val isDark = uiState.isDarkTheme
    val bgColor = if (isDark) DarkBackground else LightBackground
    val cardColor = if (isDark) DarkSurface else LightSurface
    val borderColor = if (isDark) DarkBorder else LightBorder
    val textColor = if (isDark) DarkTextPrimary else LightTextPrimary
    val textMutedColor = if (isDark) DarkTextMuted else LightTextMuted
    val context = LocalContext.current

    var nickname by remember { mutableStateOf(uiState.userProfile.nickname) }
    var bio by remember { mutableStateOf(uiState.userProfile.bio) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Text(
                        text = "Edit Profile",
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold,
                        color = textColor
                    )
                },
                navigationIcon = {
                    IconButton(onClick = { viewModel.navigateBack() }) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = "Back",
                            tint = textColor
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = cardColor)
            )
        },
        containerColor = bgColor
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .background(bgColor)
                .verticalScroll(rememberScrollState())
                .padding(16.dp)
                .testTag("edit_profile_screen"),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Profile Picture Section
            Surface(
                shape = RoundedCornerShape(16.dp),
                color = cardColor,
                border = BorderStroke(1.dp, borderColor),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(
                    modifier = Modifier.padding(20.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Box(
                        contentAlignment = Alignment.BottomEnd,
                        modifier = Modifier.size(80.dp)
                    ) {
                        Box(
                            modifier = Modifier
                                .fillMaxSize()
                                .clip(CircleShape)
                                .background(BrandBlueLight),
                            contentAlignment = Alignment.Center
                        ) {
                            Text(
                                text = nickname.take(2).uppercase(),
                                fontSize = 28.sp,
                                fontWeight = FontWeight.Bold,
                                color = BrandBlue
                            )
                        }

                        Box(
                            modifier = Modifier
                                .size(26.dp)
                                .clip(CircleShape)
                                .background(BrandBlue),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(
                                imageVector = Icons.Default.CameraAlt,
                                contentDescription = "Change avatar",
                                tint = Color.White,
                                modifier = Modifier.size(14.dp)
                            )
                        }
                    }

                    Spacer(modifier = Modifier.height(12.dp))

                    Text(
                        text = "Please select an avatar to personalize your account, supports JPG, GIF, PNG, max 5M",
                        fontSize = 11.sp,
                        color = textMutedColor,
                        lineHeight = 16.sp
                    )
                }
            }

            // Nickname Field
            Surface(
                shape = RoundedCornerShape(16.dp),
                color = cardColor,
                border = BorderStroke(1.dp, borderColor),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text("Nickname", fontSize = 13.sp, fontWeight = FontWeight.SemiBold, color = textColor)
                        Text("${nickname.length}/20", fontSize = 11.sp, color = textMutedColor)
                    }

                    Spacer(modifier = Modifier.height(8.dp))

                    OutlinedTextField(
                        value = nickname,
                        onValueChange = { if (it.length <= 20) nickname = it },
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(10.dp),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = BrandBlue,
                            unfocusedBorderColor = borderColor,
                            focusedTextColor = textColor,
                            unfocusedTextColor = textColor
                        ),
                        singleLine = true
                    )
                }
            }

            // Personal Introduction Field
            Surface(
                shape = RoundedCornerShape(16.dp),
                color = cardColor,
                border = BorderStroke(1.dp, borderColor),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text("Personal introduction", fontSize = 13.sp, fontWeight = FontWeight.SemiBold, color = textColor)
                        Text("${bio.length}/100", fontSize = 11.sp, color = textMutedColor)
                    }

                    Spacer(modifier = Modifier.height(8.dp))

                    OutlinedTextField(
                        value = bio,
                        onValueChange = { if (it.length <= 100) bio = it },
                        placeholder = { Text("Introduce your trading style or quant focus...", fontSize = 12.sp, color = textMutedColor) },
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(100.dp),
                        shape = RoundedCornerShape(10.dp),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = BrandBlue,
                            unfocusedBorderColor = borderColor,
                            focusedTextColor = textColor,
                            unfocusedTextColor = textColor
                        ),
                        maxLines = 4
                    )
                }
            }

            Spacer(modifier = Modifier.height(10.dp))

            // Save Button
            Button(
                onClick = {
                    viewModel.updateProfile(nickname.ifBlank { "user-135927" }, bio)
                    Toast.makeText(context, "Profile updated successfully", Toast.LENGTH_SHORT).show()
                    viewModel.navigateBack()
                },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(48.dp)
                    .testTag("save_profile_button"),
                shape = RoundedCornerShape(12.dp),
                colors = ButtonDefaults.buttonColors(containerColor = BrandBlue)
            ) {
                Text(
                    text = "Save",
                    fontSize = 15.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color.White
                )
            }
        }
    }
}
