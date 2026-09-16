# ruff: noqa: ARG001
import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from redis import RedisError

from src.auth.exceptions import InvalidToken

logger = logging.getLogger(__name__)


async def token_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handles invalid token errors and returns an authentication error response."""
    assert isinstance(exc, InvalidToken)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


async def redis_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, RedisError)
    logger.error("Redis error on %s %s: %s", request.method, request.url.path, exc)

    return JSONResponse(
        status_code=503,
        content={"detail": "Redis temporarily unavailable"},
    )


async def unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handles unexpected exceptions and returns a generic server error response."""
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})
