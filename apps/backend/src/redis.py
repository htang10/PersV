import redis
from src.config import settings


def redis_instance() -> redis.Redis:
    """Initiates and returns a Redis instance."""
    return redis.from_url(str(settings.REDIS_URL), decode_responses=True)
