"""Entry FastAPI SiapQuiz.

Memasang:
- middleware request_id (X-Request-ID → contextvar → response header)
- CORS (settings.cors_origin_list)
- slowapi limiter (rate limit login) + handler Problem Details
- exception handler global Problem Details (RFC 9457)
- router /api/v1
"""

import uuid
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from slowapi.errors import RateLimitExceeded
from slowapi.extension import _rate_limit_exceeded_handler
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware

from app.api.v1 import auth, health
from app.core.config import settings
from app.core.errors import register_exception_handlers
from app.core.logging import get_logger, request_id_var
from app.core.ratelimit import limiter

logger = get_logger(__name__)

REQUEST_ID_HEADER = "X-Request-ID"


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Tempelkan request_id ke contextvar dan response header."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid.uuid4())
        request_id_var.set(request_id)
        response = await call_next(request)
        response.headers[REQUEST_ID_HEADER] = request_id
        return response


def create_app() -> FastAPI:
    app = FastAPI(
        title="SiapQuiz API",
        version=settings.app_version,
        docs_url="/api/v1/docs",
        openapi_url="/api/v1/openapi.json",
    )

    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # slowapi — state limiter wajib + handler agar 429 jadi Problem Details
    app.state.limiter = limiter

    @app.exception_handler(RateLimitExceeded)
    async def ratelimit_handler(request: Request, exc: RateLimitExceeded) -> Response:
        return _rate_limit_exceeded_handler(request, exc)

    register_exception_handlers(app)
    app.include_router(health.router, prefix="/api/v1")
    app.include_router(auth.router, prefix="/api/v1")

    return app


app = create_app()
