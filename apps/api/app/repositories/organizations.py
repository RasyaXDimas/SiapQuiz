"""Repository organizations."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization


async def create(db: AsyncSession, *, name: str, type: str) -> Organization:
    org = Organization(name=name, type=type)
    db.add(org)
    await db.flush()
    return org
