from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict



class BaseComment(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_name: Optional[str] = None
    content: Optional[str] = None


class CreateComment(BaseComment):
    """Схема для создания комментария."""

    task_id: int


class UpdateComment(BaseComment):
    """Схема для обновления комментария."""

    updated_at: datetime


class CommentSchema(BaseComment):
    """Схема комментария из БД."""

    id: int
    task_id: int
    created_at: datetime
    updated_at: datetime


# ======== Межслойные DTO (Filters) ========

class CommentFilters(BaseComment):
    limit: int
    offset: int
    task_id: Optional[int] = None
    search: Optional[str] = None
    created_by: Optional[str] = None
    created_at_gte: Optional[datetime] = None
    created_at_lte: Optional[datetime] = None