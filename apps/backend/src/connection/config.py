from datetime import timedelta

from src.core.config import Settings
from src.core.rate_limiter import RateLimitRules, Scope


class ConnectionSettings(Settings):
    ENCRYPTION_KEY: str

    CACHE_CAPACITY: int = 100
    CLEANUP_PERIOD: timedelta = timedelta(minutes=30)
    CLEANUP_THRESHOLD: float = 0.3

    CONN_EXP: timedelta = timedelta(minutes=30)
    ANON_ID_LIMITS: RateLimitRules = {
        Scope.IP: "5 per 15 minutes, 15 per hour",
    }


conn_settings = ConnectionSettings  # type: ignore
