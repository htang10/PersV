import hmac
import logging
import os
import time
import uuid

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, Response
from starlette.middleware.base import RequestResponseEndpoint

from src.core.config import settings
from src.core.log import request_id_var

logger = logging.getLogger(__name__)


def register_middleware(app: FastAPI, dev_mode: bool) -> None:
    @app.middleware("http")
    async def request_context(
        request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id = uuid.uuid4().hex[:12]
        token = request_id_var.set(request_id)
        start = time.perf_counter()
        try:
            response = await call_next(request)

            logger.info(
                "%s %s %s (%.2f ms)",
                request.method,
                request.url.path,
                response.status_code,
                (time.perf_counter() - start) * 1000,
            )

            response.headers["X-Request-ID"] = request_id
            return response
        except Exception as exc:
            logger.error(
                "Unhandled %s on %s %s",
                type(exc).__name__,
                request.method,
                request.url.path,
                exc_info=exc,
            )
            response = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "detail": f"An unexpected error occurred. Reference: {request_id}"
                },
            )
        finally:
            request_id_var.reset(token)
        response.headers["X-Request-ID"] = request_id
        return response

    @app.middleware("http")
    async def proxy_secret(
        request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if (
            not dev_mode
            and request.url.path != "/health"  # startup probe has no secret
            and request.method != "OPTIONS"
        ):
            sent = request.headers.get("x-proxy-secret", "").encode()
            expected = settings.PROXY_SECRET.encode()
            if not expected or not hmac.compare_digest(sent, expected):
                return JSONResponse({"detail": "Forbidden"}, status_code=403)
        return await call_next(request)
