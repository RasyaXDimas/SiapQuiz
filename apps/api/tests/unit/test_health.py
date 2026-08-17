"""Test endpoint health & readiness.

/health tidak menyentuh dependensi; /ready bergantung Postgres & Redis,
sehingga check-nya di-mock (test unit tidak butuh container).
"""

import pytest
from fastapi.testclient import TestClient

from app.api.v1 import health
from app.main import app

client = TestClient(app)


def test_health_ok() -> None:
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "version" in body


def test_ready_ok_when_both_dependencies_up(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_postgres() -> bool:
        return True

    async def fake_redis() -> bool:
        return True

    monkeypatch.setattr(health, "_check_postgres", fake_postgres)
    monkeypatch.setattr(health, "_check_redis", fake_redis)

    resp = client.get("/api/v1/ready")
    assert resp.status_code == 200
    assert resp.json() == {"postgres": True, "redis": True}


def test_ready_503_when_postgres_down(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_postgres() -> bool:
        return False

    async def fake_redis() -> bool:
        return True

    monkeypatch.setattr(health, "_check_postgres", fake_postgres)
    monkeypatch.setattr(health, "_check_redis", fake_redis)

    resp = client.get("/api/v1/ready")
    assert resp.status_code == 503
    assert resp.json() == {"postgres": False, "redis": True}


def test_ready_503_when_redis_down(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_postgres() -> bool:
        return True

    async def fake_redis() -> bool:
        return False

    monkeypatch.setattr(health, "_check_postgres", fake_postgres)
    monkeypatch.setattr(health, "_check_redis", fake_redis)

    resp = client.get("/api/v1/ready")
    assert resp.status_code == 503
    assert resp.json() == {"postgres": True, "redis": False}
