from task_service.core.logger import get_logger, log
from task_service.infrastructure.postgres.comment_repository import CommentRepository
from task_service.infrastructure.postgres.database import Database

from task_service.schemas.comment import CommentSchema, CommentFilters

logger = get_logger(__name__)


class GetTaskCommentsUseCase:
    """Use case для получения комментариев к задаче."""

    def __init__(
            self,
            database: Database,
            repository: CommentRepository,
    )-> None:
        self._database = database
        self._repository = repository

    @log(logger)
    async def execute(
            self,
            filters: CommentFilters,
    ) -> tuple[list[CommentSchema], int]:
        """Получить список комментариев с фильтрацией"""
        async with self._database.session() as session:
            return await self._repository.get_all_comments(session=session, filters=filters)
