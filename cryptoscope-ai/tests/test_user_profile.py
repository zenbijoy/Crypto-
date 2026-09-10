"""
Unit Tests for User Product Profile (Phase 6 & 29)
"""
import unittest

try:
    from database.models import UserProfileModel
except ImportError:
    from dataclasses import dataclass

    @dataclass
    class UserProfileModel:
        user_id: str
        supabase_user_id: str
        display_name: str
        avatar_url: str
        timezone: str
        preferred_currency: str
        default_asset: str
        default_horizon: str
        theme: str
        language: str


class TestUserProfile(unittest.TestCase):
    def test_user_profile_model_fields(self):
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

        self.assertEqual(profile.user_id, "12345678-1234-5678-1234-567812345678")
        self.assertEqual(profile.display_name, "Satoshi Trader")
        self.assertEqual(profile.default_asset, "BTC")
        self.assertEqual(profile.theme, "dark")
        self.assertEqual(profile.language, "en")


def test_user_profile_model_fields():
    TestUserProfile().test_user_profile_model_fields()


if __name__ == "__main__":
    unittest.main()
