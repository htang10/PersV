import redis as redis
from redis.backoff import ExponentialWithJitterBackoff
from redis.cache import CacheConfig
from redis.retry import Retry

from src.core.config import settings

retry = Retry(backoff=ExponentialWithJitterBackoff(), retries=5)

redis_client = redis.Redis(
    username=settings.REDIS_USERNAME,
    password=settings.REDIS_PASSWORD,
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    protocol=3,
    cache_config=CacheConfig(),
    max_connections=settings.REDIS_MAX_CONN,
    decode_responses=True,
    retry=retry,
)
