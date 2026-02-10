"""
Configuration Management
Loads settings from environment variables
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""

    # AI Configuration
    AI_ENABLED: bool = False
    GEMINI_API_KEY: Optional[str] = None

    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # Analysis Configuration
    MAX_FILE_SIZE_MB: int = 10
    ANALYSIS_TIMEOUT_SECONDS: int = 300

    # Logging
    LOG_LEVEL: str = "INFO"

    # ✅ Pydantic v2 config (replaces class Config)
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    def model_post_init(self, __context) -> None:
        # Auto-enable AI if API key is present
        if self.GEMINI_API_KEY and not self.AI_ENABLED:
            self.AI_ENABLED = True


# Global settings instance
settings = Settings()
