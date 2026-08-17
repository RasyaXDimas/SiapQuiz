"""Router health & readiness.

- ``GET /api/v1/health`` — status & versi, tanpa menyentuh dependensi.
- ``GET /api/v1/ready`` — SELECT 1 ke Postgres dan PING ke Redis;
  503 bila salah satu gagal.
"""

from fastapi import APIRouter, Response, status
from sqlalchemy import text
from starlette.responses import JSONResponse

from app.core.config import settings
from app.core.db import engine
from app.core.redis import redis_client

router = APIRouter(tags=["ops"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "version": settings.app_version}


@router.get("/ready")
async def ready() -> Response:
    postgres_ok = await _check_postgres()
    redis_ok = await _check_redis()
    body = {"postgres": postgres_ok, "redis": redis_ok}
    if postgres_ok and redis_ok:
        return JSONResponse(body)
    return JSONResponse(body, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)


async def _check_postgres() -> bool:
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


async def _check_redis() -> bool:
    try:
        await redis_client.ping()
        return True
    except Exception:
        return False
