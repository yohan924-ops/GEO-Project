"""Application settings loaded from environment (.env)."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # API keys (optional in test mode)
    openai_api_key: str | None = None
    google_api_key: str | None = None
    anthropic_api_key: str | None = None

    # Database
    database_url: str = "sqlite:///./geo.db"

    # Test mode: no real LLM calls (template prompts + mock adapters)
    geo_test_mode: bool = True

    # Provider models
    search_model_openai: str = "gpt-4o"
    search_model_gemini: str = "gemini-2.0-flash"
    search_model_anthropic: str = "claude-sonnet-4-6"
    gen_model_anthropic: str = "claude-opus-4-8"

    # Scale
    keyword_count: int = 100
    question_count: int = 100
    provider_concurrency: int = 5


@lru_cache
def get_settings() -> Settings:
    return Settings()
