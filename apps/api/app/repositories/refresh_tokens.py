"""Repository refresh_tokens."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken


async def create(
    db: AsyncSession,
    *,
    user_id: UUID,
    token_hash: str,
    expires_at: datetime,
    user_agent: str | None,
) -> RefreshToken:
    token = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
        user_agent=user_agent,
    )
    db.add(token)
    await db.flush()
    return token


async def get_by_hash(db: AsyncSession, *, token_hash: str) -> RefreshToken | None:
    stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    return (await db.execute(stmt)).scalar_one_or_none()


async def mark_revoked(
    db: AsyncSession, *, token: RefreshToken, replaced_by_id: UUID | None = None
) -> None:
    await db.execute(
        update(RefreshToken)
        .where(RefreshToken.id == token.id)
        .values(
            revoked_at=datetime.now(UTC),
            replaced_by_id=replaced_by_id,
        )
    )


async def revoke_all_for_user(db: AsyncSession, *, user_id: UUID) -> None:
    """Cabut seluruh token aktif milik user (deteksi pemakaian ulang)."""
    await db.execute(
        update(RefreshToken)
        .where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
        .values(revoked_at=datetime.now(UTC))
    )


async def delete_expired(db: AsyncSession, *, user_id: UUID) -> None:
    await db.execute(
        delete(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.expires_at < datetime.now(UTC),
        )
    )
