"""
应用配置管理
使用 Pydantic Settings 进行环境变量管理和验证
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """应用配置类"""

    # OpenAI Configuration
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4-turbo"
    OPENAI_TEMPERATURE: float = 0.7

    # Google API Configuration
    GOOGLE_PROJECT_ID: str
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str

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

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    def is_production(self) -> bool:
        """检查是否为生产环境"""
        return self.APP_ENV == "production"

    def is_development(self) -> bool:
        """检查是否为开发环境"""
        return self.APP_ENV == "development"


# 全局配置实例
settings = Settings()