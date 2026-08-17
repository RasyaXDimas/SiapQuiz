"""Test format error Problem Details (RFC 9457) — AC-SETUP-07.

Endpoint tak dikenal → 404 application/problem+json lengkap dengan
type, title, status, detail, code, request_id.
"""

from fastapi import APIRouter
from fastapi.testclient import TestClient

from app.core.errors import DomainError
from app.main import app, create_app

client = TestClient(app)


class BoomError(DomainError):
    code = "BOOM"
    status = 422
    title = "Meledak"


def _make_app_with(router: APIRouter) -> TestClient:
    test_app = create_app()
    test_app.include_router(router, prefix="/api/v1")
    return TestClient(test_app)


def test_unknown_endpoint_returns_problem_details() -> None:
    resp = client.get("/api/v1/tidak-ada")
    assert resp.status_code == 404
    assert resp.headers["content-type"].startswith("application/problem+json")

    body = resp.json()
    assert body["type"] == "https://siapquiz.app/errors/not-found"
    assert body["title"] == "Not Found"
    assert body["status"] == 404
    assert body["code"] == "NOT_FOUND"
    assert "detail" in body
    assert body["request_id"] != ""


def test_domain_error_becomes_problem_details() -> None:
    router = APIRouter()

    @router.get("/test-domain-error")
    async def trigger() -> None:
        raise BoomError("detail uji")

    test_client = _make_app_with(router)
    resp = test_client.get("/api/v1/test-domain-error")
    assert resp.status_code == 422
    body = resp.json()
    assert body["code"] == "BOOM"
    assert body["detail"] == "detail uji"
    assert body["status"] == 422
    assert body["request_id"] != ""


def test_validation_error_becomes_problem_details() -> None:
    router = APIRouter()

    @router.get("/needs-int/{value}")
    async def needs_int(value: int) -> dict[str, int]:
        return {"value": value}

    test_client = _make_app_with(router)
    resp = test_client.get("/api/v1/needs-int/abc")
    assert resp.status_code == 422
    body = resp.json()
    assert body["code"] == "VALIDATION_ERROR"
    assert body["status"] == 422
    assert body["request_id"] != ""
