"""Test logging: redaksi nilai sensitif dan request_id di response header."""

import structlog
from fastapi.testclient import TestClient

from app.core.logging import redact_sensitive
from app.main import app

client = TestClient(app)


def test_redact_sensitive_removes_values() -> None:
    logger = structlog.get_logger("test")
    event = {
        "event": "test",
        "user": "budi",
        "password": "rahasia",
        "api_key": "sk-123",
        "nested": {"authorization": "Bearer xxx", "safe": "ok"},
    }
    result = redact_sensitive(logger, "info", event)
    assert result["password"] == "[REDACTED]"
    assert result["api_key"] == "[REDACTED]"
    assert result["nested"]["authorization"] == "[REDACTED]"
    assert result["nested"]["safe"] == "ok"
    assert result["user"] == "budi"


def test_redact_sensitive_handles_plain_message() -> None:
    logger = structlog.get_logger("test")
    # event_dict bisa berupa string bila event tanpa kwargs
    result = redact_sensitive(logger, "info", {"event": "ping.received", "job_id": 1})
    assert result["job_id"] == 1


def test_request_id_returned_in_response_header() -> None:
    resp = client.get("/api/v1/health", headers={"X-Request-ID": "test-123"})
    assert resp.status_code == 200
    assert resp.headers["X-Request-ID"] == "test-123"


def test_request_id_generated_when_missing() -> None:
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.headers["X-Request-ID"] != ""
