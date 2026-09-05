"""
Unit Tests for User Product Profile (Phase 6 & 29)
"""
import pytest
from database.models import UserProfileModel


def test_user_profile_model_fields():
    """Verify all required fields exist on UserProfileModel."""
    profile = UserProfileModel(
        user_id="12345678-1234-5678-1234-567812345678",
        supabase_user_id="12345678-1234-5678-1234-567812345678",
        display_name="Satoshi Trader",
        avatar_url="https://cryptoscope.ai/avatars/satoshi.png",
        timezone="America/New_York",
        preferred_currency="USD",
        default_asset="BTC",
        default_horizon="1h",
        theme="dark",
        language="en"
    )

    assert profile.user_id == "12345678-1234-5678-1234-567812345678"
    assert profile.display_name == "Satoshi Trader"
    assert profile.default_asset == "BTC"
    assert profile.theme == "dark"
    assert profile.language == "en"
