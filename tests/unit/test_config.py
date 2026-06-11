"""
Unit tests for config module — Settings, logging config
"""

import pytest
import os
from unittest.mock import patch


class TestSettings:
    """Test application settings"""

    def test_default_settings(self):
        from config.settings import Settings
        s = Settings()
        assert s.APP_ENV == "development"
        assert s.LOG_LEVEL == "INFO"
        assert s.DEFAULT_TIMEZONE == "Asia/Shanghai"
        assert s.OPENAI_BASE_URL == "https://api.deepseek.com/v1"
        assert s.EMAIL_NOTIFICATION_ENABLED is True

    def test_get_llm_api_key_deepseek_first(self):
        from config.settings import Settings
        s = Settings(DEEPSEEK_API_KEY="sk-ds", OPENAI_API_KEY="sk-oai")
        assert s.get_llm_api_key() == "sk-ds"

    def test_get_llm_api_key_openai_fallback(self):
        from config.settings import Settings
        s = Settings(OPENAI_API_KEY="sk-oai")
        assert s.get_llm_api_key() == "sk-oai"

    def test_get_llm_api_key_none(self):
        from config.settings import Settings
        # Override .env values explicitly
        s = Settings(DEEPSEEK_API_KEY="", OPENAI_API_KEY="")
        assert s.get_llm_api_key() == ""

    def test_get_llm_model_deepseek(self):
        from config.settings import Settings
        s = Settings(DEEPSEEK_API_KEY="sk-ds", OPENAI_API_KEY="")
        assert s.get_llm_model() == "deepseek-chat"

    def test_get_llm_model_openai_fallback(self):
        from config.settings import Settings
        # Explicitly set all LLM-related fields to isolate the test
        s = Settings(
            DEEPSEEK_API_KEY="",
            OPENAI_API_KEY="sk-oai",
            DEEPSEEK_MODEL="deepseek-chat",
            OPENAI_MODEL="gpt-4-turbo",
        )
        assert s.get_llm_model() == "gpt-4-turbo"

    def test_is_production(self):
        from config.settings import Settings
        assert Settings(APP_ENV="production").is_production() is True
        assert Settings(APP_ENV="development").is_production() is False

    def test_is_development(self):
        from config.settings import Settings
        assert Settings(APP_ENV="development").is_development() is True
        assert Settings(APP_ENV="production").is_development() is False

    def test_get_openai_base_url(self):
        from config.settings import Settings
        s = Settings()
        assert s.get_openai_base_url() == "https://api.deepseek.com/v1"
