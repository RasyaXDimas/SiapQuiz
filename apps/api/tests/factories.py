"""Factory data uji — user & organisasi untuk test tenancy dan auth.

Setiap fungsi menerima db session dan mengembalikan objek model yang sudah
di-flush. Digunakan test tenancy (dua organisasi) dan AC-AUTH.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.organization import Organization
from app.models.user import User


async def make_organization(
    db: AsyncSession, *, name: str = "Ruang kerja Uji", type: str = "PERSONAL"
) -> Organization:
    org = Organization(name=name, type=type)
    db.add(org)
    await db.flush()
    return org


async def make_user(
    db: AsyncSession,
    *,
    organization: Organization,
    email: str | None = None,
    display_name: str = "Pengguna Uji",
    role: str = "TEACHER",
    password: str = "password-uji-123",
    is_active: bool = True,
) -> User:
    user = User(
        organization_id=organization.id,
        email=email or f"{uuid.uuid4().hex[:10]}@example.com",
        password_hash=hash_password(password),
        display_name=display_name,
        role=role,
        is_active=is_active,
    )
    db.add(user)
    await db.flush()
    return user
