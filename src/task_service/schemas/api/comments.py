from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from task_service.schemas.api.pagination import PaginationAwareRequest


class CommentResponse(BaseModel):
    """Ответ с данными комментария"""

    id: int
    task_id: int
    user_name: str
    content: str
    created_at: datetime
    updated_at: datetime

class CommentRequest(PaginationAwareRequest):
    """Запрос списка комментариев с фильтрацией"""

    task_id: Optional[int] = None
    user_name: Optional[str] = None
    created_at_gte: Optional[datetime] = None
    created_at_lte: Optional[datetime] = None


class CreateCommentRequestPayload(BaseModel):
    """Payload для создания комментария"""

    task_id: int
    content: str