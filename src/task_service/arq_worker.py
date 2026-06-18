from arq import cron
from arq.connections import RedisSettings

from task_service.core.config import settings
from task_service.infrastructure.redis.auto_escalate_tasks import escalate_old_pending_tasks


class WorkerSettings:
    """Настройка ARQ Worker с CRON"""

    redis_settings = RedisSettings(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        database=settings.REDIS_DB,
        password=settings.REDIS_PASSWORD,
    )
    allow_abort_jobs = True

    cron_jobs = [
        cron(
            escalate_old_pending_tasks,
            name="escalate_old_pending_tasks",
            hour=9,
        ),
    ]