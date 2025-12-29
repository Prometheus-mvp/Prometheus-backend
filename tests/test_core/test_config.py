"""Tests for app.core.config module."""

from unittest.mock import patch
from app.core.config import Settings


def test_settings_from_env():
    """Test settings loading from environment."""
    with patch.dict(
        "os.environ",
        {
            "SUPABASE_URL": "https://test.supabase.co",
            "SUPABASE_ANON_KEY": "test-anon-key",
            "SUPABASE_SERVICE_ROLE_KEY": "test-service-key",
            "DATABASE_URL": "postgresql://test:test@localhost/test",
            "REDIS_URL": "redis://localhost:6379/0",
            "OPENAI_API_KEY": "sk-test",
            "ENCRYPTION_KEY": "a" * 64,
            "SLACK_CLIENT_ID": "slack-id",
            "SLACK_CLIENT_SECRET": "slack-secret",
            "SLACK_REDIRECT_URI": "http://localhost/callback",
            "TELEGRAM_API_ID": "12345",
            "TELEGRAM_API_HASH": "telegram-hash",
            "OUTLOOK_CLIENT_ID": "outlook-id",
            "OUTLOOK_CLIENT_SECRET": "outlook-secret",
            "OUTLOOK_REDIRECT_URI": "http://localhost/outlook",
            "OUTLOOK_TENANT_ID": "common",
            "ENVIRONMENT": "production",
            "LOG_LEVEL": "INFO",
            "API_HOST": "0.0.0.0",
            "API_PORT": "8000",
        },
    ):
        settings = Settings()
        assert settings.supabase_url == "https://test.supabase.co"
        assert settings.database_url == "postgresql://test:test@localhost/test"
        assert settings.environment == "production"
        assert settings.is_production is True
        assert settings.is_development is False


def test_settings_defaults():
    """Test settings default values."""
    with patch.dict(
        "os.environ",
        {
            "SUPABASE_URL": "https://test.supabase.co",
            "SUPABASE_ANON_KEY": "test-anon-key",
            "SUPABASE_SERVICE_ROLE_KEY": "test-service-key",
            "DATABASE_URL": "postgresql://test:test@localhost/test",
            "REDIS_URL": "redis://localhost:6379/0",
            "OPENAI_API_KEY": "sk-test",
            "ENCRYPTION_KEY": "a" * 64,
            "SLACK_CLIENT_ID": "slack-id",
            "SLACK_CLIENT_SECRET": "slack-secret",
            "SLACK_REDIRECT_URI": "http://localhost/callback",
            "TELEGRAM_API_ID": "12345",
            "TELEGRAM_API_HASH": "telegram-hash",
            "OUTLOOK_CLIENT_ID": "outlook-id",
            "OUTLOOK_CLIENT_SECRET": "outlook-secret",
            "OUTLOOK_REDIRECT_URI": "http://localhost/outlook",
        },
    ):
        settings = Settings()
        assert settings.outlook_tenant_id == "common"
        assert settings.environment == "development"
        assert settings.log_level == "INFO"
        assert settings.api_host == "0.0.0.0"
        assert settings.api_port == 8000


def test_is_development():
    """Test is_development property."""
    with patch.dict(
        "os.environ",
        {
            "SUPABASE_URL": "https://test.supabase.co",
            "SUPABASE_ANON_KEY": "test-anon-key",
            "SUPABASE_SERVICE_ROLE_KEY": "test-service-key",
            "DATABASE_URL": "postgresql://test:test@localhost/test",
            "REDIS_URL": "redis://localhost:6379/0",
            "OPENAI_API_KEY": "sk-test",
            "ENCRYPTION_KEY": "a" * 64,
            "SLACK_CLIENT_ID": "slack-id",
            "SLACK_CLIENT_SECRET": "slack-secret",
            "SLACK_REDIRECT_URI": "http://localhost/callback",
            "TELEGRAM_API_ID": "12345",
            "TELEGRAM_API_HASH": "telegram-hash",
            "OUTLOOK_CLIENT_ID": "outlook-id",
            "OUTLOOK_CLIENT_SECRET": "outlook-secret",
            "OUTLOOK_REDIRECT_URI": "http://localhost/outlook",
            "ENVIRONMENT": "development",
        },
    ):
        settings = Settings()
        assert settings.is_development is True
        assert settings.is_production is False
