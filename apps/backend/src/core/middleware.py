import hmac
import os

from fastapi import Request
from fastapi.responses import JSONResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from src.core.config import settings


class ProxySecretMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if (
            os.getenv("ENVIRONMENT") == "production"
            and request.url.path != "/health"  # startup probe has no secret
            and request.method != "OPTIONS"
        ):
            sent = request.headers.get("x-proxy-secret", "").encode()
            expected = settings.PROXY_SECRET.encode()
            if not expected or not hmac.compare_digest(sent, expected):
                return JSONResponse({"detail": "Forbidden"}, status_code=403)
        return await call_next(request)
