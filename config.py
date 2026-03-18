"""
Application configuration via pydantic-settings.

All settings are loaded from environment variables (and .env file).
"""

from __future__ import annotations


from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    env: str = "development"
    app_url: str = "https://qr.spoo.me"
    app_name: str = "QR Code Generator API"
    host: str = "0.0.0.0"
    port: int = 8080

    # CORS
    cors_origins: list[str] = ["*"]

    # QR code limits
    qr_max_size: int = 1000
    qr_min_size: int = 10

    @property
    def is_production(self) -> bool:
        return self.env == "production"
