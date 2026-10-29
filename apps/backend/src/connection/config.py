from datetime import timedelta

from src.core.config import Settings


class PipelineSettings(Settings):
    ENCRYPTION_KEY: str

    CACHE_CAPACITY: int = 100
    CLEANUP_PERIOD: timedelta = timedelta(minutes=30)
    CLEANUP_THRESHOLD: float = 0.3

    AUTH_CONN_EXP: timedelta = timedelta(minutes=15)
    ANON_CONN_EXP: timedelta = timedelta(minutes=30)


pl_settings = PipelineSettings()  # type: ignore
