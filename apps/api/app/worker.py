"""Entry worker arq SiapQuiz.

Dijalankan dengan: ``arq app.worker.WorkerSettings``
Redis diambil dari settings (env-config.md), bukan hardcode.
"""

from typing import Any, ClassVar

from arq.connections import RedisSettings

from app.core.config import settings
from app.core.logging import get_logger
from app.tasks.health import ping

logger = get_logger(__name__)

MAX_JOBS = 10
JOB_TIMEOUT = 300


async def on_startup(ctx: dict[str, Any]) -> None:
    # ctx arq hanya memuat redis + job_timeout (tidak selalu ada max_jobs);
    # pakai .get dengan fallback ke nilai WorkerSettings.
    logger.info(
        "worker.started",
        max_jobs=ctx.get("max_jobs", MAX_JOBS),
        job_timeout=ctx.get("job_timeout", JOB_TIMEOUT),
    )


class WorkerSettings:
    functions: ClassVar[list[Any]] = [ping]
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
    max_jobs = MAX_JOBS
    job_timeout = JOB_TIMEOUT
    keep_result = 3600
    on_startup = on_startup
