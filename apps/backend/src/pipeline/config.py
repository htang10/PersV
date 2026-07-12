from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class PipelineSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    OPENAI_API_KEY: str
    DEMO_DB_URL: PostgresDsn


pl_settings = PipelineSettings()
