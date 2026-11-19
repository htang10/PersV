import logging

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.exception_handlers import http_exception_handler
from redis import RedisError

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RedisError)
    async def redis_exception_handler(request: Request, exc: RedisError) -> Response:
        logger.error(
            "Redis error on %s %s", request.method, request.url.path, exc_info=exc
        )
        http_exc = HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Redis is temporarily unavailable.",
        )
        return await http_exception_handler(request, http_exc)
