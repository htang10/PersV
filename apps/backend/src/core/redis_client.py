import redis.asyncio as redis
from redis.asyncio.retry import Retry
from redis.backoff import ExponentialWithJitterBackoff

from src.core.config import settings

retry = Retry(backoff=ExponentialWithJitterBackoff(), retries=5)

redis_client = redis.Redis(
    username=settings.REDIS_USERNAME,
    password=settings.REDIS_PASSWORD,
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    protocol=3,
    max_connections=settings.REDIS_MAX_CONN,
    decode_responses=True,
    retry=retry,
)
