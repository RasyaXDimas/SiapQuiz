"""Repository users."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


async def get_by_email(db: AsyncSession, *, email: str) -> User | None:
    """Cari user berdasarkan email (global — email UNIQUE case-insensitive)."""
    stmt = select(User).where(User.email == email)
    return (await db.execute(stmt)).scalar_one_or_none()


async def get_by_id(db: AsyncSession, *, user_id: UUID, organization_id: UUID) -> User | None:
    """Ambil user milik organisasi tertentu — tenant scoping wajib (FR-AUTH-06)."""
    stmt = select(User).where(User.id == user_id, User.organization_id == organization_id)
    return (await db.execute(stmt)).scalar_one_or_none()


async def create(
    db: AsyncSession,
    *,
    organization_id: UUID,
    email: str,
    password_hash: str,
    display_name: str,
    role: str,
) -> User:
    user = User(
        organization_id=organization_id,
        email=email,
        password_hash=password_hash,
        display_name=display_name,
        role=role,
    )
    db.add(user)
    await db.flush()
    return user


async def update_last_login(db: AsyncSession, *, user_id: UUID) -> None:
    await db.execute(update(User).where(User.id == user_id).values(last_login_at=datetime.now(UTC)))
