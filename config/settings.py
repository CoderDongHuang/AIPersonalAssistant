"""
Application Configuration Management
Uses Pydantic Settings for environment variable management and validation
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings class"""

    # LLM Configuration (DeepSeek compatible with OpenAI SDK)
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_MODEL: str = "deepseek-chat"

    # OpenAI Compatible Configuration
    OPENAI_BASE_URL: str = "https://api.deepseek.com/v1"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4-turbo"
    OPENAI_TEMPERATURE: float = 0.7

    # Application Settings
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    DEFAULT_TIMEZONE: str = "Asia/Shanghai"

    # Database (for production checkpoint storage)
    DATABASE_URL: Optional[str] = None

    # Calendar Settings
    CALENDAR_MAX_EVENTS: int = 50
    CONFLICT_CHECK_HOURS: int = 2

    # Email Settings
    EMAIL_NOTIFICATION_ENABLED: bool = True
    EMAIL_SMTP_SERVER: str = ""
    EMAIL_SMTP_PORT: int = 587
    EMAIL_SENDER: str = ""
    EMAIL_PASSWORD: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    def get_llm_api_key(self) -> str:
        """Get LLM API key (prefer DeepSeek, fallback to OpenAI)"""
        return self.DEEPSEEK_API_KEY or self.OPENAI_API_KEY

    def get_llm_model(self) -> str:
        """Get LLM model name"""
        if self.DEEPSEEK_API_KEY:
            return self.DEEPSEEK_MODEL
        return self.OPENAI_MODEL

    def get_openai_base_url(self) -> str:
        """Get OpenAI-compatible API base URL"""
        return self.OPENAI_BASE_URL

    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.APP_ENV == "production"

    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.APP_ENV == "development"


# Global settings instance
settings = Settings()
