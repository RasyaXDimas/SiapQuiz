"""Format error standar SiapQuiz: RFC 9457 Problem Details.

Satu exception handler global (dipasang di main.py) mengubah DomainError,
HTTPException, dan RequestValidationError menjadi application/problem+json
dengan field ``type``, ``title``, ``status``, ``detail``, ``code``,
``request_id`` (system-design.md §12).
"""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import get_logger, request_id_var

logger = get_logger(__name__)

ERRORS_BASE_URL = "https://siapquiz.app/errors"


class DomainError(Exception):
    """Kelas dasar error domain. Subclass menetapkan code/status/title."""

    code: str = "DOMAIN_ERROR"
    status: int = 500
    title: str = "Terjadi kesalahan"

    def __init__(self, detail: str | None = None) -> None:
        self.detail = detail or self.title
        super().__init__(self.detail)


def _problem_response(
    *, status: int, type_: str, title: str, detail: str, code: str
) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={
            "type": type_,
            "title": title,
            "status": status,
            "detail": detail,
            "code": code,
            "request_id": request_id_var.get(),
        },
        media_type="application/problem+json",
    )


def _slugify(code: str) -> str:
    return code.lower().replace("_", "-")


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
        logger.warning(
            "error.domain",
            code=exc.code,
            status=exc.status,
            detail=exc.detail,
            path=request.url.path,
        )
        return _problem_response(
            status=exc.status,
            type_=f"{ERRORS_BASE_URL}/{_slugify(exc.code)}",
            title=exc.title,
            detail=exc.detail,
            code=exc.code,
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        code = _http_status_code(exc.status_code)
        logger.warning(
            "error.http",
            status=exc.status_code,
            detail=exc.detail,
            path=request.url.path,
        )
        return _problem_response(
            status=exc.status_code,
            type_=f"{ERRORS_BASE_URL}/{_slugify(code)}",
            title=code.replace("_", " ").title(),
            detail=str(exc.detail),
            code=code,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        logger.warning(
            "error.validation",
            errors=exc.errors(),
            path=request.url.path,
        )
        return _problem_response(
            status=422,
            type_=f"{ERRORS_BASE_URL}/validation-error",
            title="Permintaan tidak valid",
            detail="Satu atau lebih field tidak memenuhi kontrak.",
            code="VALIDATION_ERROR",
        )


def _http_status_code(status: int) -> str:
    """Petakan status HTTP ke kode stabil ala kebab (404 → NOT_FOUND)."""
    mapping: dict[int, str] = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        409: "CONFLICT",
        422: "UNPROCESSABLE_ENTITY",
        429: "TOO_MANY_REQUESTS",
        500: "INTERNAL_SERVER_ERROR",
        503: "SERVICE_UNAVAILABLE",
    }
    return mapping.get(status, f"HTTP_{status}")


__all__ = ["ERRORS_BASE_URL", "DomainError", "register_exception_handlers"]
