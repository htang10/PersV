# ruff: noqa: ARG001
from fastapi import Request
from fastapi.responses import JSONResponse

from src.auth.exceptions import InvalidToken


async def token_error_handler(request: Request, exc: InvalidToken) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


async def unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})
