from dishka import FromDishka
from fastapi import APIRouter, Depends, HTTPException
from dishka.integrations.fastapi import inject
from starlette import status

from task_service.core.logger import get_logger, log
from task_service.schemas.api.comments import CommentResponse, CommentRequest, CreateCommentRequestPayload
from task_service.schemas.api.pagination import Pagination
from task_service.domain.use_cases.get_task_comments import GetTaskCommentsUseCase
from task_service.schemas.comment import CommentFilters,CreateComment
from task_service.domain.use_cases.create_comment import CreateCommentUseCase

from task_service.api.depends import get_current_user
from task_service.schemas.auth import AccessTokenData

logger = get_logger(__name__)

comments_router = APIRouter(prefix="/comments")


@comments_router.get(
    "",
    response_model=Pagination[CommentResponse],
)
@inject
@log(logger)
async def get_all_comments(
        use_case: FromDishka[GetTaskCommentsUseCase],
        request: CommentRequest = Depends(),
) -> Pagination[CommentResponse]:
    """Получить список задач с фильтрацией и пагинацией"""
    try:
        records, total = await use_case.execute(
            filters=CommentFilters.model_validate(request.model_dump()),
        )
        return Pagination(limit=request.limit, offset=request.offset, items=records, total=total)
    except Exception as e:
        logger.error(f"Exception getting comments: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@comments_router.post(
    "",
    response_model=CommentResponse,
)
@inject
@log(logger)
async def create_comment(
        use_case: FromDishka[CreateCommentUseCase],
        payload: CreateCommentRequestPayload = Depends(),
        current_user: AccessTokenData = Depends(get_current_user),
) -> CommentResponse:
    """Создать комментарий к задаче"""
    try:
        return CommentResponse(
            await use_case.execute(
                comment = CreateComment(user_name=current_user.username, **payload.model_dump()),
            )
        )
    except Exception as e:
        logger.error(f"Exception creating comments: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))