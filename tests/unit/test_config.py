"""Unit tests for config — application settings."""

from config import AppSettings


class TestAppSettings:
    def test_defaults(self):
        settings = AppSettings()
        assert settings.app_name == "QR Code Generator API"
        assert settings.host == "0.0.0.0"
        assert settings.port == 8080
        assert settings.qr_max_size == 1000
        assert settings.qr_min_size == 10

    def test_is_production(self):
        settings = AppSettings(env="production")
        assert settings.is_production is True

    def test_is_not_production(self):
        settings = AppSettings(env="development")
        assert settings.is_production is False

    def test_cors_defaults(self):
        settings = AppSettings()
        assert settings.cors_origins == ["*"]
