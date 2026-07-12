from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from src.auth.dependencies import auth_engine
from src.auth.exceptions import InvalidToken
from src.auth.routers import router as auth_router
from src.core.config import settings
from src.core.handlers import (
    token_error_handler,
    unexpected_error_handler,
)
from src.core.log import setup_logging
from src.pipeline.routers import connection, query


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:  # noqa: ARG001
    setup_logging("DEBUG" if settings.DEBUG else "INFO")
    yield
    auth_engine.dispose()


app = FastAPI(lifespan=lifespan)
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(connection.router, prefix="/pipeline", tags=["pipeline"])
app.include_router(query.router, prefix="/pipeline", tags=["pipeline"])

app.add_exception_handler(InvalidToken, token_error_handler)
app.add_exception_handler(Exception, unexpected_error_handler)
