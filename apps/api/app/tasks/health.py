"""Task arq health: ping sederhana untuk memverifikasi antrean bekerja."""

from typing import Any

from app.core.logging import get_logger

logger = get_logger(__name__)


async def ping(ctx: dict[str, Any]) -> str:
    logger.info("ping.received", job_id=ctx["job_id"])
    return "pong"
