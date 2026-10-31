"""
Limits are declared per scope, such as email address, IP address and user id.
Counting uses a sliding window counter, with state kept in Redis so limits
hold across server instances. Exceeding any limit rejects the request with 429.
"""

from enum import StrEnum

from fastapi import HTTPException, status
from limits import RateLimitItem, parse_many
from limits.storage import RedisStorage
from limits.strategies import SlidingWindowCounterRateLimiter

from src.core.config import settings
from src.core.utils import get_redis_url


class Scope(StrEnum):
    """What a limit is counted against."""

    EMAIL = "email"
    IP = "ip"
    USER_ID = "user_id"


RateLimitRules = dict[Scope, str]  # Limit expressions per scope, e.g. {Scope.IP: "5/minute"}
LimitKeys = list[tuple[RateLimitItem, str]]  # Each limit paired with its counter key


class _PlainKeyRedisStorage(RedisStorage):
    """A class inheriting `RedisStorage` with overridden methods."""

    def _current_window_key(self, key: str) -> str:
        """Returns the key unchanged, without the curly braces the base class adds."""
        return key


_storage = _PlainKeyRedisStorage(uri=get_redis_url(), key_prefix="limits")
_limiter = SlidingWindowCounterRateLimiter(_storage)


def _rate_limit_exceeded() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail="Too many attempts. Try again later.",
    )


class Attempt:
    """The counter keys of one request, ready to be counted.

    Returned by `RateLimiter.check()`. Call `record()` once the outcome of the
    request is known.
    """

    def __init__(self, keys: LimitKeys) -> None:
        self.keys = keys  # Empty when rate limiting is disabled

    def record(self) -> None:
        """Counts one hit against every limit rule under the specified scope from `RateLimiter`."""
        for key in self.keys:
            _limiter.hit(*key)


class RateLimiter:
    """A named set of limits, each applied to one scope.

    Use `check()` and `record()` when only some outcomes should count (e.g.
    failed logins). Use `consume()` when every request counts.
    """

    def __init__(self, namespace: str, rules: RateLimitRules) -> None:
        """
        Args:
            namespace: Name that keeps this limiter's counters separate from others.
            rules: Limit expressions per scope. A scope may hold several limits.
        """
        self.rules: list[tuple[Scope, RateLimitItem]] = []
        for scope, expression in rules.items():
            for item in parse_many(expression):
                item.namespace = namespace
                self.rules.append((scope, item))
        self.required_scopes = {scope.value for scope in rules}

    def check(self, **identifiers: str) -> Attempt:
        """Verifies no limit is exhausted, without counting the request.

        Args:
            **identifiers: One value per scope, keyed by scope name.

        Returns:
            An `Attempt` to `record()` once the outcome is known.

        Raises:
            HTTPException: 429 if any limit is exhausted.
            ValueError: If the identifiers do not match the limiter's scopes.
        """
        keys = self._keys(identifiers)
        for key in keys:
            if not _limiter.test(*key):
                raise _rate_limit_exceeded()
        return Attempt(keys)

    def consume(self, **identifiers: str) -> None:
        """Counts the request and rejects it if any limit is exceeded.

        Args:
            **identifiers: One value per scope, keyed by scope name.

        Raises:
            HTTPException: 429 if any limit is exceeded by this request.
            ValueError: If the identifiers do not match the limiter's scopes.
        """
        for key in self._keys(identifiers):
            if not _limiter.hit(*key):
                raise _rate_limit_exceeded()

    def _keys(self, identifiers: dict[str, str]) -> LimitKeys:
        """Builds the counter key of every limit for the given identifiers."""
        if set(identifiers) != self.required_scopes:
            raise ValueError(
                f"Expected identifiers {sorted(self.required_scopes)}, got {sorted(identifiers)}"
            )
        if not settings.RATE_LIMIT_ENABLED:
            return []
        return [
            (item, f":{scope.value}:{identifiers[scope.value]}:")
            for scope, item in self.rules
        ]