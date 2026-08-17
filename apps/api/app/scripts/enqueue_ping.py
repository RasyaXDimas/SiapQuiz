"""Antrikan task ``ping`` secara manual untuk verifikasi worker.

Jalankan: uv run python -m app.scripts.enqueue_ping
"""

import asyncio

from arq.connections import ArqRedis, RedisSettings, create_pool

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


async def main() -> None:
    redis: ArqRedis = await create_pool(RedisSettings.from_dsn(settings.redis_url))
    job = await redis.enqueue_job("ping")
    if job is None:
        logger.error("ping.enqueue_failed")
        return
    logger.info("ping.enqueued", job_id=job.job_id)
    await redis.aclose()


if __name__ == "__main__":
    asyncio.run(main())
