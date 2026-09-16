import asyncio
import contextlib
import logging
import sys
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from redis import RedisError

from src.auth.dependencies import AUTH_ENGINE
from src.auth.exceptions import InvalidToken
from src.auth.routers import router as auth_router
from src.core.config import settings
from src.core.handlers import (
    redis_exception_handler,
    token_error_handler,
    unexpected_error_handler,
)
from src.core.health import check_health
from src.core.log import setup_logging
from src.core.redis_client import redis_client
from src.pipeline.database import DEMO_ENGINE
from src.pipeline.routers import connection, query
from src.pipeline.tasks import sweep_stale_connections

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:  # noqa: ARG001
    setup_logging(10 if settings.DEBUG else 20)
    if settings.DEBUG:
        logger.info("Debug mode enabled.")
    else:
        logger.info("Debug mode disabled.")
    health = check_health()
    if health.status == "unhealthy":
        if not settings.DEBUG:
            logger.critical("Health check failed at startup. Shutting down.")
            sys.exit(1)
        logger.warning("Health check failed at startup. Skipping health check.")
    sweep_task = asyncio.create_task(sweep_stale_connections())
    yield
    sweep_task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await sweep_task
    redis_client.close()
    AUTH_ENGINE.dispose()
    DEMO_ENGINE.dispose()


app = FastAPI(lifespan=lifespan)
app.add_api_route("/health", endpoint=check_health, tags=["health"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(connection.router, prefix="/pipeline", tags=["pipeline"])
app.include_router(query.router, prefix="/pipeline", tags=["pipeline"])

app.add_exception_handler(InvalidToken, token_error_handler)
app.add_exception_handler(RedisError, redis_exception_handler)
app.add_exception_handler(Exception, unexpected_error_handler)
