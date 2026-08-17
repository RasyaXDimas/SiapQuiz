"""Test endpoint auth — mencakup AC-AUTH-01..07, 10 (yang dapat diuji tanpa
resource ber-tenant dari sprint berikutnya).

Dijalankan via TestClient dengan DB test (fixture ``client`` di conftest).
"""

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.models.organization import Organization
from app.models.user import User


def _reg_payload(email: str, *, role: str = "TEACHER", password: str = "rahasia-123") -> dict:
    return {
        "email": email,
        "password": password,
        "display_name": "Uji",
        "role": role,
    }


async def test_register_teacher_creates_personal_org(client: TestClient, session) -> None:
    resp = client.post("/api/v1/auth/register", json=_reg_payload("guru@example.com"))
    assert resp.status_code == 201
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert body["user"]["role"] == "TEACHER"
    assert "access_token" in body

    org = (
        (await session.execute(select(Organization).where(Organization.type == "PERSONAL")))
        .scalars()
        .first()
    )
    assert org is not None
    assert org.name == "Ruang kerja Uji"

    user = (
        await session.execute(select(User).where(User.email == "guru@example.com"))
    ).scalar_one()
    assert user.organization_id == org.id
    set_cookie = resp.headers.get("set-cookie", "")
    assert "refresh_token=" in set_cookie
    assert "HttpOnly" in set_cookie


def test_register_duplicate_email_conflict(client: TestClient, session) -> None:
    client.post("/api/v1/auth/register", json=_reg_payload("dupe@example.com"))
    resp = client.post("/api/v1/auth/register", json=_reg_payload("dupe@example.com"))
    assert resp.status_code == 409
    body = resp.json()
    assert body["code"] == "EMAIL_EXISTS"
    assert "sudah terdaftar" in body["detail"]


def test_register_short_password_422(client: TestClient, session) -> None:
    payload = _reg_payload("short@example.com")
    payload["password"] = "1234567"  # 7 karakter
    resp = client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 422


async def test_login_sets_httponly_cookie_and_argon2_hash(client: TestClient, session) -> None:
    client.post("/api/v1/auth/register", json=_reg_payload("login@example.com"))
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": "rahasia-123"},
    )
    assert resp.status_code == 200
    assert "refresh_token=" in resp.headers.get("set-cookie", "")

    user = (
        await session.execute(select(User).where(User.email == "login@example.com"))
    ).scalar_one()
    assert user.password_hash.startswith("$argon2id$")
    assert user.last_login_at is not None


def test_login_wrong_password_401(client: TestClient, session) -> None:
    client.post("/api/v1/auth/register", json=_reg_payload("wrong@example.com"))
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "wrong@example.com", "password": "salah-password"},
    )
    assert resp.status_code == 401
    assert resp.json()["code"] == "INVALID_CREDENTIALS"


def test_refresh_rotation_old_token_rejected(client: TestClient, session) -> None:
    client.post("/api/v1/auth/register", json=_reg_payload("rot@example.com"))
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "rot@example.com", "password": "rahasia-123"},
    )
    old_cookie = login_resp.headers["set-cookie"].split(";")[0].split("=")[1]

    refresh1 = client.post("/api/v1/auth/refresh")
    assert refresh1.status_code == 200
    assert "refresh_token=" in refresh1.headers.get("set-cookie", "")

    # Pakai cookie LAMA lagi → ditolak (AC-AUTH-06)
    client.cookies.set("refresh_token", old_cookie)
    refresh2 = client.post("/api/v1/auth/refresh")
    assert refresh2.status_code == 401


def test_logout_revokes_refresh(client: TestClient, session) -> None:
    reg = client.post("/api/v1/auth/register", json=_reg_payload("logout@example.com"))
    access = reg.json()["access_token"]
    old_cookie = reg.headers["set-cookie"].split(";")[0].split("=")[1]

    logout = client.post("/api/v1/auth/logout", headers={"Authorization": f"Bearer {access}"})
    assert logout.status_code == 204

    client.cookies.set("refresh_token", old_cookie)
    resp = client.post("/api/v1/auth/refresh")
    assert resp.status_code == 401


def test_me_returns_user_without_password_hash(client: TestClient, session) -> None:
    reg = client.post("/api/v1/auth/register", json=_reg_payload("me@example.com"))
    access = reg.json()["access_token"]
    resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {access}"})
    assert resp.status_code == 200
    body = resp.json()
    assert "password_hash" not in body
    assert body["email"] == "me@example.com"
