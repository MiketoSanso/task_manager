from task_service.core.logger import log
from task_service.infrastructure.postgres.database import Database
from task_service.infrastructure.postgres.task_repository import TaskRepository, logger
from task_service.infrastructure.redis.repository import RedisRepository
from task_service.schemas.api.tasks import TaskStatisticsResponse


class GetTaskStatisticsUseCase:
    """Use case для получения статистики задач"""

    def __init__(
        self,
        database: Database,
        repository: TaskRepository,
        cache: RedisRepository
    ) -> None:
        self._database = database
        self._repository = repository
        self._cache = cache

    @log(logger)
    async def execute(self) -> TaskStatisticsResponse:
        async with self._database.session() as session:
            count_tasks = await self._repository.get_total_tasks_count(session=session)
            tasks_by_status = await self._repository.get_tasks_count_by_status(session=session)
            tasks_by_priority = await self._repository.get_tasks_count_by_priority(session=session)
            tasks_by_assignee = await self._repository.get_tasks_count_by_assignee(session=session)

            result = TaskStatisticsResponse(
                total_tasks = count_tasks,
                by_status = tasks_by_status,
                by_priority = tasks_by_priority,
                by_assignee = tasks_by_assignee
            )

        await self._cache.set_task_statistics(statistics=result, ex=60)
        logger.debug(f"Cache miss: task statistics")


