from task_service.core.logger import get_logger, log

from task_service.infrastructure.postgres.database import Database
from task_service.infrastructure.postgres.comment_repository import CommentRepository
from task_service.schemas.comment import CreateComment, CommentSchema

logger = get_logger(__name__)

class CreateCommentUseCase:
    """Use case для создания комментария."""

    def __init__(
            self,
            database: Database,
            repository: CommentRepository,
    ):
        self._database = database
        self._repository = repository

    @log(logger)
    async def execute(self, comment: CreateComment) -> CommentSchema:
        async with self._database.session() as session:
            created_comment = await self._repository.create_comment(session, comment)

        logger.info(f"Comment created: id={created_comment.id}, content={created_comment.content}")
        return created_comment