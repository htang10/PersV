from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class PipelineSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    ANTHROPIC_API_KEY: str
    DEMO_DB_URL: PostgresDsn
    DEMO_SCHEMA: str
    ENCRYPTION_KEY: str
    CONN_EXP: int


pl_settings = PipelineSettings()  # type: ignore
