from datetime import timedelta

from src.core.config import Settings


class AuthSettings(Settings):
    CREDENTIAL_HMAC_SECRET_KEY: str

    MAX_USER_SESSIONS: int

    ANON_ID_EXP: timedelta
    OTP_EXP: timedelta
    ACCESS_TOKEN_EXP: timedelta
    REFRESH_TOKEN_EXP: timedelta

    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    FROM_EMAIL: str

    JWT_SECRET_KEY: str
    JWT_ISSUER: str
    JWT_AUDIENCE: str
    JWT_ALGORITHM: str

    OTP_GENERATION_THROTTLE: str
    LOGIN_THROTTLE: str
    ANON_ID_THROTTLE: str


auth_settings = AuthSettings()  # type: ignore
