import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=f".env.{os.getenv('ENVIRONMENT', 'development')}",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    DEBUG: bool
    RATE_LIMIT_ENABLED: bool

    PG_HOST: str
    PG_PORT: int
    PG_DATABASE: str
    PG_SSL_MODE: str | None = None
    PG_CHANNEL_BINDING: str | None = None

    PG_DEMO_USER: str
    PG_DEMO_PASSWORD: str
    PG_AUTH_USER: str
    PG_AUTH_PASSWORD: str

    PG_DEMO_SCHEMA: str

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_USERNAME: str
    REDIS_PASSWORD: str
    REDIS_MAX_CONN: int
    REDIS_CONN_TIMEOUT: int


settings = Settings()  # type: ignore
