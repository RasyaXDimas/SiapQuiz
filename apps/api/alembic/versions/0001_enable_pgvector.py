"""0001_enable_pgvector — aktifkan ekstensi vector (pgvector).

Sprint 0: belum ada tabel domain. Migrasi ini hanya mengaktifkan ekstensi
yang dipakai kolom embedding mulai Sprint 2. upgrade() harus idempoten
(IF NOT EXISTS) karena ekstensi mungkin sudah aktif di image postgres.
"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")


def downgrade() -> None:
    op.execute("DROP EXTENSION IF EXISTS vector")
