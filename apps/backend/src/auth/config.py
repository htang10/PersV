from datetime import timedelta

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    AUTH_DB_URL: PostgresDsn

    ANON_ID_EXP: timedelta

    OTP_EXP: timedelta
    OTP_SECRET_KEY: str

    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    FROM_EMAIL: str

    JWT_SECRET_KEY: str
    JWT_ISSUER: str
    JWT_AUDIENCE: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXP: timedelta
    REFRESH_TOKEN_EXP: timedelta

    OTP_GENERATION_THROTTLE: str
    LOGIN_THROTTLE: str
    ANON_SESSION_THROTTLE: str


auth_settings = AuthSettings()  # type: ignore
