"""Fixture pytest — database test terisolasi + migrasi Alembic + TestClient.

Test dijalankan lewat ``docker compose exec api uv run pytest`` agar
``postgres`` terjangkau dari jaringan compose. DB test (siapquiz_test) dibuat
dan dimigrasi sekali per sesi.

- Migrasi dijalankan sebagai SUBPROCESS terpisah (python -m alembic) karena
  env.py memanggil ``asyncio.run``.
- Engine dibuat function-scoped agar terikat event loop test yang sama.
- ``client`` (TestClient sync) membuat engine per-request dengan NullPool di
  dalam loop TestClient sendiri, sehingga asyncpg tidak bercampur loop.
"""

import asyncio
import os
import subprocess
import sys
from collections.abc import AsyncIterator, Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.db import get_db
from app.main import create_app

# Host di dalam compose: postgres. Override via env bila perlu.
ADMIN_URL = os.getenv(
    "ADMIN_DATABASE_URL",
    "postgresql+asyncpg://siapquiz:ganti-password-ini@postgres:5432/postgres",
)
TEST_DB_NAME = "siapquiz_test"
TEST_DB_URL = f"postgresql+asyncpg://siapquiz:ganti-password-ini@postgres:5432/{TEST_DB_NAME}"


async def _ensure_database() -> None:
    admin_engine = create_async_engine(ADMIN_URL, isolation_level="AUTOCOMMIT")
    async with admin_engine.connect() as conn:
        exists = await conn.scalar(
            text(f"SELECT 1 FROM pg_database WHERE datname = '{TEST_DB_NAME}'")
        )
        if exists:
            await conn.execute(text(f"DROP DATABASE {TEST_DB_NAME}"))
        await conn.execute(text(f"CREATE DATABASE {TEST_DB_NAME}"))
    await admin_engine.dispose()


def _run_migrations() -> None:
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env = {**os.environ, "DATABASE_URL": TEST_DB_URL}
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=project_root,
        env=env,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Migrasi test gagal:\n{result.stdout}\n{result.stderr}")


@pytest.fixture(scope="session")
def db_setup() -> None:
    """Buat + migrasi DB test sekali per sesi (sync context → aman asyncio.run)."""
    asyncio.run(_ensure_database())
    _run_migrations()


@pytest.fixture
async def engine(db_setup):
    """Engine function-scoped — terikat event loop test yang sama."""
    eng = create_async_engine(TEST_DB_URL)
    yield eng
    await eng.dispose()


@pytest.fixture
async def session(engine) -> AsyncIterator[AsyncSession]:
    maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with maker() as s:
        for table in ("refresh_tokens", "audit_logs", "users", "organizations"):
            await s.execute(text(f"DELETE FROM {table}"))
        await s.commit()
        yield s


@pytest.fixture
def client(db_setup) -> Iterator[TestClient]:
    """TestClient sync dengan get_db di-override; engine per-request (NullPool)."""

    async def _override_get_db() -> AsyncIterator[AsyncSession]:
        eng = create_async_engine(TEST_DB_URL, poolclass=NullPool)
        maker = async_sessionmaker(eng, class_=AsyncSession, expire_on_commit=False)
        try:
            async with maker() as s:
                yield s
        finally:
            await eng.dispose()

    app = create_app()
    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
