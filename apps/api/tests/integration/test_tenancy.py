"""Test isolasi tenant — FR-AUTH-06 / AC-AUTH-08.

Inti: akses sumber daya milik organisasi lain ditolak (repository mengembalikan
None → endpoint membalas 404, bukan 403). Test di-parametrisasi atas daftar
resource sehingga sprint berikutnya cukup menambah satu baris parameter.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import users as users_repo
from tests.factories import make_organization, make_user


@pytest.mark.parametrize("method,path", [])
def test_cross_tenant_isolation_parametrized(client, method: str, path: str) -> None:
    """Struktur terparametrisasi; daftar (method, path) diisi sprint berikutnya."""
    resp = getattr(client, method.lower())(path)
    assert resp.status_code == 404, "Akses lintas tenant harus 404, bukan 403"


async def test_repository_tenant_filter_returns_none(session: AsyncSession) -> None:
    """Guru A tidak dapat mengambil user guru B (FR-AUTH-06 → 404)."""
    org_a = await make_organization(session, name="Org A")
    org_b = await make_organization(session, name="Org B")
    user_a = await make_user(session, organization=org_a, email="a@example.com")
    user_b = await make_user(session, organization=org_b, email="b@example.com")
    await session.commit()

    got_a = await users_repo.get_by_id(session, user_id=user_a.id, organization_id=org_a.id)
    assert got_a is not None

    cross = await users_repo.get_by_id(session, user_id=user_b.id, organization_id=org_a.id)
    assert cross is None
