"""Entry FastAPI SiapQuiz.

Memasang:
- middleware request_id (baca X-Request-ID atau buat UUID baru → contextvar →
  response header) — AC-SETUP-06
- exception handler global Problem Details (RFC 9457) — system-design.md §12
- router /api/v1
"""

import uuid
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.v1 import health
from app.core.config import settings
from app.core.errors import register_exception_handlers
from app.core.logging import get_logger, request_id_var

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
    register_exception_handlers(app)
    app.include_router(health.router, prefix="/api/v1")

    return app


app = create_app()
