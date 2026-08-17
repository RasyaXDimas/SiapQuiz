"""Keamanan SiapQuiz: argon2id, JWT access, refresh token rotasi.

FR-AUTH-02 (argon2id), FR-AUTH-04 (JWT 15 menit + refresh 30 hari cookie),
FR-AUTH-05 (rotasi refresh token).
"""

import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.errors import DomainError
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.repositories import refresh_tokens as rt_repo

ph = PasswordHasher()


class InvalidCredentialsError(DomainError):
    code, status, title = "INVALID_CREDENTIALS", 401, "Email atau password salah"


class RefreshTokenInvalidError(DomainError):
    code, status, title = "REFRESH_TOKEN_INVALID", 401, "Sesi tidak valid"


class TokenPayload(BaseModel):
    """Payload access token JWT (klaim: sub, role, org_id, jti, exp)."""

    sub: str
    role: str
    org_id: str
    jti: str
    exp: int


def hash_password(plain: str) -> str:
    return ph.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return ph.verify(hashed, plain)
    except (VerifyMismatchError, Exception):
        return False


def create_access_token(user: User) -> tuple[str, int]:
    """Terbitkan JWT access; kembalikan (token, expires_in_detik)."""
    now = datetime.now(UTC)
    expires_in = settings.access_token_ttl_minutes * 60
    payload = {
        "sub": str(user.id),
        "role": user.role,
        "org_id": str(user.organization_id),
        "jti": str(uuid4()),
        "exp": now + timedelta(minutes=settings.access_token_ttl_minutes),
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token, expires_in


def decode_access_token(token: str) -> TokenPayload:
    try:
        data = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return TokenPayload(**data)
    except jwt.PyJWTError:
        raise InvalidCredentialsError() from None


def _hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


async def create_refresh_token(
    db: AsyncSession, *, user_id: UUID, user_agent: str | None
) -> tuple[str, RefreshToken]:
    """Buat refresh token acak 32 byte; simpan hash SHA-256; kembalikan mentah."""
    raw = secrets.token_urlsafe(32)
    expires_at = datetime.now(UTC) + timedelta(days=settings.refresh_token_ttl_days)
    token = await rt_repo.create(
        db,
        user_id=user_id,
        token_hash=_hash_token(raw),
        expires_at=expires_at,
        user_agent=user_agent,
    )
    return raw, token


async def rotate_refresh_token(
    db: AsyncSession, *, raw_token: str, user_agent: str | None
) -> tuple[str, User]:
    """R otasi refresh token; deteksi pemakaian ulang → cabut seluruh rantai."""
    token = await rt_repo.get_by_hash(db, token_hash=_hash_token(raw_token))

    if token is None or token.expires_at < datetime.now(UTC):
        raise RefreshTokenInvalidError()

    if token.revoked_at is not None:
        await rt_repo.revoke_all_for_user(db, user_id=token.user_id)
        await db.commit()
        raise RefreshTokenInvalidError()

    user = (await db.execute(select(User).where(User.id == token.user_id))).scalar_one_or_none()
    if user is None or not user.is_active:
        raise RefreshTokenInvalidError()

    raw_new, token_new = await create_refresh_token(db, user_id=user.id, user_agent=user_agent)
    await rt_repo.mark_revoked(db, token=token, replaced_by_id=token_new.id)
    return raw_new, user
