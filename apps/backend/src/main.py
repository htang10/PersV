import asyncio
import contextlib
import logging
import os
import sys
from contextlib import asynccontextmanager
from typing import AsyncIterator

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute

from src.auth.dependencies import AUTH_ENGINE
from src.auth.routers import router as auth_router
from src.connection.database import DEMO_ENGINE
from src.connection.routers import connection, query
from src.connection.tasks import sweep_stale_connections
from src.core.config import settings
from src.core.handlers import register_exception_handlers
from src.core.health import check_health
from src.core.log import setup_logging
from src.core.redis_client import redis_client
from src.core.responses import APIResponse
from src.profile.routers import router as profile_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:  # noqa: ARG001
    setup_logging(10 if settings.DEBUG else 20)
    if not settings.DEBUG:
        logger.info("Debug mode disabled.")
        health = check_health()
        if health.status == "unhealthy":
            if not settings.DEBUG:
                logger.critical("Health check failed at startup. Shutting down.")
                sys.exit(1)
            logger.warning("Health check failed at startup. Skipping health check.")
    else:
        logger.info("Debug mode enabled.")
    sweep_task = asyncio.create_task(sweep_stale_connections())
    yield
    sweep_task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await sweep_task
    redis_client.close()
    AUTH_ENGINE.dispose()
    DEMO_ENGINE.dispose()


def generate_unique_op_id(route: APIRoute) -> str:
    return f"{route.methods} - {route.path}"


app = FastAPI(
    lifespan=lifespan,
    default_response_class=APIResponse,
    generate_unique_id_function=generate_unique_op_id,
)

# CORS
origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-New-Access-Token"],
)

# Routers
app.add_api_route("/health", endpoint=check_health, tags=["health"])
app.include_router(auth_router, prefix="/auth", tags=["authentication"])
app.include_router(connection.router, prefix="/connection", tags=["connection"])
app.include_router(query.router, prefix="/connection", tags=["connection"])
app.include_router(profile_router, prefix="/users", tags=["profile"])

# Global exception handlers
register_exception_handlers(app=app)

# # Allow deployment environments to override the default worker count
workers_count = int(os.getenv("WEB_CONCURRENCY", 5))
if workers_count < 1:
    raise ValueError("WEB_CONCURRENCY must be at least 1")

if __name__ == "__main__":
    is_prod: bool = os.getenv("ENVIRONMENT") == "production"
    uvicorn.run(
        "src.main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        workers=(
            workers_count if is_prod else 1
        ),  # Disable multiprocessing during development
        reload=(not is_prod),  # Disable server reload on changes when deployed
        http="httptools",
        access_log=False,
        proxy_headers=False,  # No proxy in front, skip Uvicorn's X-Forwarded-* middleware
        server_header=False,
        timeout_keep_alive=75,  # Keep idle connections open for at least 75s
        backlog=4096,
    )
