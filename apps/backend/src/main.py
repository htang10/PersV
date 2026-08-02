import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from pipeline.tasks import sweep_stale_connections
from src.auth.dependencies import AUTH_ENGINE
from src.auth.exceptions import InvalidToken
from src.auth.routers import router as auth_router
from src.core.config import settings
from src.core.handlers import (
    token_error_handler,
    unexpected_error_handler,
)
from src.core.log import setup_logging
from src.pipeline.database import DEMO_ENGINE
from src.pipeline.routers import connection, query


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:  # noqa: ARG001
    setup_logging("DEBUG" if settings.DEBUG else "INFO")
    sweep_task = asyncio.create_task(sweep_stale_connections())
    yield
    AUTH_ENGINE.dispose()
    DEMO_ENGINE.dispose()
    sweep_task.cancel()


app = FastAPI(lifespan=lifespan)
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(connection.router, prefix="/pipeline", tags=["pipeline"])
app.include_router(query.router, prefix="/pipeline", tags=["pipeline"])

app.add_exception_handler(InvalidToken, token_error_handler)
app.add_exception_handler(Exception, unexpected_error_handler)
