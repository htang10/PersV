from fastapi import HTTPException, status
from limits import storage, strategies

from src.core.config import settings

limits_storage = storage.RedisStorage(str(settings.REDIS_URL))
limiter = strategies.SlidingWindowCounterRateLimiter(limits_storage)

LimitSpec = list[tuple]  # (limit, namespace, scope, identifier)


def check_limits(limits: LimitSpec) -> None:
    """Raises 429 if any of the given limits are already exhausted."""
    for limit, namespace, scope, identifier in limits:
        if not limiter.test(limit, namespace, scope, identifier):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many attempts. Try again later.",
            )


def record_hits(limits: LimitSpec) -> None:
    """Increments all given limits (call after a failed/consumed attempt)."""
    for limit, namespace, scope, identifier in limits:
        limiter.hit(limit, namespace, scope, identifier)
