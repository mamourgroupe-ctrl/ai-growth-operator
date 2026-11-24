from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql://localhost/ai_growth_operator"
    app_database_url: str = "postgresql://localhost/ai_growth_operator"
    session_ttl_minutes: int = 60 * 24 * 14
    session_absolute_days: int = 30
    cookie_secure: bool = True

    model_config = SettingsConfigDict(env_prefix="AGO_", env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
