from typing import Type

from sqlalchemy import insert, and_, select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from task_service.core.logger import get_logger, log
from task_service.schemas.comment import CommentSchema, CreateComment, CommentFilters
from task_service.infrastructure.postgres.models import Comment


logger = get_logger(__name__)


class CommentRepository:
    """Репозиторий для работы с комментариями"""

    _comments_collection: Type[Comment] = Comment

    @log(logger)
    async def create_comment(
            self,
            session: AsyncSession,
            comment: CreateComment,
    )-> CommentSchema:
        values = comment.model_dump()
        query = insert(self._comments_collection).values(values).returning(self._comments_collection)
        result = await session.scalar(query)
        return CommentSchema.model_validate(result)

    @log(logger)
    async def get_all_comments(
            self,
            session: AsyncSession,
            filters: CommentFilters,
    )-> tuple[list[CommentSchema], int]:
        query_filters = self._build_filters(filters)

        query = (
            select(self._comments_collection)
            .where(and_(*query_filters))
            .limit(filters.limit)
            .offset(filters.offset)
            .order_by(self._comments_collection.created_at.desc())
        )

        db_rows = await session.scalars(query)

        count_query = select(func.count(self._comments_collection.id.distinct())).where(and_(*query_filters))
        total = await session.scalar(count_query)

        return [CommentSchema.model_validate(obj=obj) for obj in db_rows.all()], total or 0

    def _build_filters(self, filters: CommentFilters) -> list:
        """Построить фильтры для запроса"""
        filters_list = []

        if filters.search:
            search_pattern = f"%{filters.search}%"
            filters_list.append(
                self._comments_collection.content.ilike(search_pattern),
            )

        if filters.task_id:
            filters_list.append(self._comments_collection.task_id == filters.task_id)

        if filters.created_by:
            filters_list.append(self._comments_collection.created_by == filters.created_by)

        if filters.created_at_gte:
            filters_list.append(self._comments_collection.created_at >= filters.created_at_gte)

        if filters.created_at_lte:
            filters_list.append(self._comments_collection.created_at <= filters.created_at_lte)

        return filters_list