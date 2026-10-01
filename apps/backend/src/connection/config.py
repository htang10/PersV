from datetime import timedelta

from src.core.config import Settings


class PipelineSettings(Settings):
    ENCRYPTION_KEY: str

    AUTH_CONN_EXP: timedelta
    ANON_CONN_EXP: timedelta

    CACHE_CAPACITY: int
    CLEANUP_PERIOD: timedelta
    CLEANUP_THRESHOLD: float


pl_settings = PipelineSettings()  # type: ignore
