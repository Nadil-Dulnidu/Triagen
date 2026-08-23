"""Unit tests for application configuration."""

from __future__ import annotations

from server.config import Settings


def test_settings_defaults() -> None:
    """Test default settings instantiation and properties."""
    settings = Settings(
        _env_file=None,
        clerk_secret_key="sk_test_123",
        clerk_webhook_secret="whsec_123",
        clerk_jwks_url="https://test.clerk.dev/.well-known/jwks.json",
    )
    assert settings.app_title == "PullSense API"
    assert settings.rate_limit_reviews_per_hour == 100
    assert settings.gcp_region == "us-central1"
    assert settings.gemini_flash_model == "gemini-2.5-flash"
    assert settings.gemini_pro_model == "gemini-2.5-pro"
