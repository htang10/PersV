from redis import Redis
from redis.backoff import ExponentialWithJitterBackoff
from redis.cache import CacheConfig
from redis.connection import BlockingConnectionPool
from redis.maint_notifications import MaintNotificationsConfig
from redis.retry import Retry

from src.core.config import settings

retry = Retry(backoff=ExponentialWithJitterBackoff(), retries=5)

# Clients wait for an available connection from the pool instead of
# raising error
connection_pool = BlockingConnectionPool(
    username=settings.REDIS_USERNAME,
    password=settings.REDIS_PASSWORD,
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    protocol=3,
    max_connections=settings.REDIS_MAX_CONN,
    timeout=settings.REDIS_CONN_TIMEOUT,
    retry=retry,
    cache_config=CacheConfig(),
    decode_responses=True,
    maint_notifications_config=MaintNotificationsConfig(enabled=False),
)

redis_client = Redis(
    connection_pool=connection_pool,
)
