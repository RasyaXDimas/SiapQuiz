"""Endpoint autentikasi /api/v1/auth — register, login, refresh, logout, me.

Mengikuti kontrak api-spec.yaml dan AC-AUTH-01..10. Error lintas tenant → 404,
bukan 403 (FR-AUTH-06).
"""

import hashlib
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_db
from app.core.deps import CurrentUser
from app.core.errors import DomainError
from app.core.ratelimit import limiter, login_email_key, login_ip_key
from app.core.security import (
    InvalidCredentialsError,
    RefreshTokenInvalidError,
    create_access_token,
    create_refresh_token,
    hash_password,
    rotate_refresh_token,
    verify_password,
)
from app.models.user import User
from app.repositories import organizations as org_repo
from app.repositories import refresh_tokens as rt_repo
from app.repositories import users as users_repo
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest, UserOut
from app.services import audit_service

router = APIRouter(prefix="/auth", tags=["auth"])

REFRESH_COOKIE = "refresh_token"


class EmailAlreadyExists(DomainError):
    code, status, title = "EMAIL_EXISTS", 409, "Email sudah terdaftar"


def _set_refresh_cookie(response: Response, value: str) -> None:
    response.set_cookie(
        key=REFRESH_COOKIE,
        value=value,
        httponly=True,
        samesite=settings.cookie_samesite,
        secure=settings.cookie_secure,
        path="/",
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(key=REFRESH_COOKIE, path="/")


def _user_agent(request: Request) -> str | None:
    return request.headers.get("user-agent")


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


async def _issue_session(
    db: AsyncSession, user: User, response: Response, request: Request
) -> AuthResponse:
    access_token, expires_in = create_access_token(user)
    refresh_raw, _ = await create_refresh_token(
        db, user_id=user.id, user_agent=_user_agent(request)
    )
    _set_refresh_cookie(response, refresh_raw)
    return AuthResponse(
        access_token=access_token,
        expires_in=expires_in,
        user=UserOut.from_user(user),
    )


@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(
    body: RegisterRequest,
    request: Request,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AuthResponse:
    existing = await users_repo.get_by_email(db, email=body.email)
    if existing is not None:
        raise EmailAlreadyExists("Email ini sudah terdaftar. Coba masuk.")

    # Buat organisasi PERSONAL untuk SEMUA peran (kolom tak pernah null)
    org = await org_repo.create(db, name=f"Ruang kerja {body.display_name}", type="PERSONAL")
    user = await users_repo.create(
        db,
        organization_id=org.id,
        email=body.email,
        password_hash=hash_password(body.password),
        display_name=body.display_name,
        role=body.role,
    )

    await audit_service.record(
        db,
        organization_id=org.id,
        actor_user_id=user.id,
        action="user.registered",
        entity_type="user",
        entity_id=user.id,
        metadata={"role": user.role},
        ip_address=request.client.host if request.client else None,
    )

    session = await _issue_session(db, user, response, request)
    await db.commit()
    return session


@router.post("/login", response_model=AuthResponse)
@limiter.limit(settings.ratelimit_login, key_func=login_ip_key)
@limiter.limit(settings.ratelimit_login, key_func=login_email_key)
async def login(
    request: Request,
    body: LoginRequest,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AuthResponse:
    user = await users_repo.get_by_email(db, email=body.email)
    if user is None or not verify_password(body.password, user.password_hash):
        raise InvalidCredentialsError("Email atau password salah")

    await users_repo.update_last_login(db, user_id=user.id)
    await audit_service.record(
        db,
        organization_id=user.organization_id,
        actor_user_id=user.id,
        action="user.logged_in",
        entity_type="user",
        entity_id=user.id,
        ip_address=request.client.host if request.client else None,
    )

    session = await _issue_session(db, user, response, request)
    await db.commit()
    return session


@router.post("/refresh", response_model=AuthResponse)
async def refresh(
    request: Request,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AuthResponse:
    raw_token = request.cookies.get(REFRESH_COOKIE)
    if not raw_token:
        raise RefreshTokenInvalidError()

    raw_new, user = await rotate_refresh_token(
        db, raw_token=raw_token, user_agent=_user_agent(request)
    )
    _set_refresh_cookie(response, raw_new)
    access_token, expires_in = create_access_token(user)
    await db.commit()
    return AuthResponse(
        access_token=access_token,
        expires_in=expires_in,
        user=UserOut.from_user(user),
    )


@router.post("/logout", status_code=204)
async def logout(
    request: Request,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: CurrentUser,
) -> Response:
    raw_token = request.cookies.get(REFRESH_COOKIE)
    if raw_token:
        token = await rt_repo.get_by_hash(db, token_hash=_sha256(raw_token))
        if token is not None and token.user_id == user.id:
            await rt_repo.mark_revoked(db, token=token)
    await audit_service.record(
        db,
        organization_id=user.organization_id,
        actor_user_id=user.id,
        action="user.logged_out",
        entity_type="user",
        entity_id=user.id,
        ip_address=request.client.host if request.client else None,
    )
    _clear_refresh_cookie(response)
    await db.commit()
    return Response(status_code=204)


@router.get("/me", response_model=UserOut)
async def me(user: CurrentUser) -> UserOut:
    return UserOut.from_user(user)
