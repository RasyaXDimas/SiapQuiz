"""Dependency autentikasi & konteks tenant SiapQuiz.

get_current_user (Authorization bearer → user), get_tenant_context
(TenantContext), require_role (factory pembatas peran).
"""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.errors import DomainError
from app.core.security import decode_access_token
from app.models.user import User
from app.repositories import users as users_repo


class UnauthorizedError(DomainError):
    code, status, title = "UNAUTHORIZED", 401, "Belum masuk"


class ForbiddenError(DomainError):
    code, status, title = "FORBIDDEN", 403, "Tidak diizinkan"


@dataclass
class TenantContext:
    user_id: UUID
    organization_id: UUID
    role: str


def _extract_token(authorization: str | None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise UnauthorizedError()
    return authorization.removeprefix("Bearer ")


async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    authorization: Annotated[str | None, Header()] = None,
) -> User:
    payload = decode_access_token(_extract_token(authorization))
    user = await users_repo.get_by_id(
        db, user_id=UUID(payload.sub), organization_id=UUID(payload.org_id)
    )
    if user is None or not user.is_active:
        raise UnauthorizedError()
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_tenant_context(
    user: Annotated[User, Depends(get_current_user)],
) -> TenantContext:
    return TenantContext(user_id=user.id, organization_id=user.organization_id, role=user.role)


def require_role(*roles: str) -> Callable[..., Awaitable[User]]:
    """Factory dependency — tolak bila peran user tidak termasuk roles."""

    async def _dependency(
        user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        if user.role not in roles:
            raise ForbiddenError()
        return user

    return _dependency
