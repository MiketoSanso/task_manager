from datetime import datetime, timezone

from task_service.core.logger import setup_logging, get_logger
from task_service.core.providers.setup import container
from task_service.domain.use_cases.get_tasks import GetTasksUseCase
from task_service.domain.use_cases.update_task import UpdateTaskUseCase
from task_service.schemas.task import UpdateTask, TaskFilters, TaskStatus

logger = get_logger(__name__)

async def escalate_old_pending_tasks(ctx):
    """CRON задача для эскалации задач."""
    setup_logging()
    logger.info("Starting send_pending_notifications_task")

    async with container() as nested_container:
        use_case = await nested_container.get(GetTasksUseCase)

        tasks = use_case.execute_for_escalation()

        use_case = await nested_container.get(UpdateTaskUseCase)

        for task in tasks:
            update_data = UpdateTask()
            time = datetime.now(timezone.utc).isoformat()
            use_case.execute(task=update_data ,task_id=task.id, updated_by=time)

    logger.info(f"escalate_old_pending_tasks completed.")

