from fastapi import HTTPException, status
from limits import storage, strategies

from src.auth.config import auth_settings
from src.core.utils import get_redis_url

limits_storage = storage.RedisStorage(get_redis_url())
limiter = strategies.SlidingWindowCounterRateLimiter(limits_storage)

LimitSpec = list[tuple]  # (limit, namespace, scope, identifier)


def check_limits(limits: LimitSpec) -> None:
    """Raises 429 if any of the given limits are already exhausted."""
    if auth_settings.RATE_LIMIT_ENABLED:
        for limit, namespace, scope, identifier in limits:
            if not limiter.test(limit, namespace, scope, identifier):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many attempts. Try again later.",
                )


def record_hits(limits: LimitSpec) -> None:
    """Increments all given limits (call after a failed/consumed attempt)."""
    if auth_settings.RATE_LIMIT_ENABLED:
        for limit, namespace, scope, identifier in limits:
            limiter.hit(limit, namespace, scope, identifier)
