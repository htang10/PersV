from datetime import timedelta

from src.core.config import Settings
from src.core.rate_limiter import RateLimitRules, Scope


class AuthSettings(Settings):
    CREDENTIAL_HMAC_SECRET_KEY: str

    OTP_EXP: timedelta = timedelta(minutes=10)

    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    FROM_EMAIL: str

    REFRESH_TOKEN_EXP: timedelta = timedelta(days=7)
    MAX_USER_SESSIONS: int = 3
    ANON_ID_EXP: timedelta = timedelta(minutes=15)

    ACCESS_TOKEN_EXP: timedelta = timedelta(minutes=15)

    JWT_ALGORITHM: str = "HS256"
    JWT_SECRET_KEY: str
    JWT_ISSUER: str = "persv-api"
    JWT_AUDIENCE: str = "persv-client"

    OTP_LIMITS: RateLimitRules = {
        Scope.EMAIL: "3 per 10 minutes, 10 per hour",
        Scope.IP: "9 per 10 minutes, 20 per hour",
        Scope.USER_ID: "5 per hour",  # Email change's specific policy
    }
    EMAIL_VERIFICATION_LIMITS: RateLimitRules = {
        Scope.EMAIL: "5 per 5 minutes, 20 per hour",
        Scope.IP: "15 per 10 minutes, 30 per hour",
    }
    ANON_ID_LIMITS: RateLimitRules = {
        Scope.IP: "5 per 15 minutes, 15 per hour",
    }
    EMAIL_CHANGE_LIMITS: RateLimitRules = {
        Scope.USER_ID: "1 per 30 days",
    }


auth_settings = AuthSettings()  # type: ignore
