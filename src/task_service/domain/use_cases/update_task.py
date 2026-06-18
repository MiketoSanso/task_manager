from datetime import datetime, timedelta, timezone

from task_service.core.logger import get_logger, log
from task_service.infrastructure.postgres.database import Database
from task_service.infrastructure.postgres.task_repository import TaskRepository
from task_service.infrastructure.rabbitmq.publisher import RabbitMQPublisher
from task_service.infrastructure.redis.repository import RedisRepository
from task_service.infrastructure.kafka.publisher import KafkaPublisher
from task_service.schemas.task import (
    TaskEventType,
    TaskNotificationMessage,
    TaskSchema,
    UpdateTask, TaskStatus, TaskPriority,
)

logger = get_logger(__name__)


class UpdateTaskUseCase:
    """Use case для обновления задачи."""

    def __init__(
        self,
        database: Database,
        repository: TaskRepository,
        publisher: RabbitMQPublisher,
        cache: RedisRepository,
        kafka_publisher: KafkaPublisher,
    ) -> None:
        self._database = database
        self._repository = repository
        self._publisher = publisher
        self._cache = cache
        self._kafka_publisher = kafka_publisher

    @log(logger)
    async def execute(
        self,
        task: UpdateTask,
        task_id: int,
        updated_by: str,
    ) -> TaskSchema:
        """Обновить задачу и отправить уведомление."""
        async with (self._database.session() as session):
            old_task = await self._repository.get_one_task(session, task_id)

            now = datetime.now(timezone.utc).replace(tzinfo=None)

            new_update_task = task
            if old_task.status == TaskStatus.TODO and now - old_task.updated_at > timedelta(days=3) and old_task.priority != TaskPriority.CRITICAL:
                priority_map = {
                    TaskPriority.LOW: TaskPriority.MEDIUM,
                    TaskPriority.MEDIUM: TaskPriority.HIGH,
                    TaskPriority.HIGH: TaskPriority.CRITICAL,
                }
                new_update_task = UpdateTask(priority=priority_map[old_task.priority])

            updated_task = await self._repository.update_task(session, task_id, new_update_task)

        # Обновляем кэш
        await self._cache.delete_task(task_id)
        await self._cache.set_task(updated_task)

        event_type = self.__detect_event_type()

        # Отправляем уведомление в RabbitMQ (для нотификаций)
        notification = TaskNotificationMessage(
            task_id=updated_task.id,
            event_type=event_type,
            task_title=updated_task.title,
            task_description=updated_task.description,
            assignee=updated_task.assignee,
            status=updated_task.status,
            priority=updated_task.priority,
            created_by=updated_by,
        )
        await self._publisher.publish_task_notification(notification)

        # Отправляем событие в Kafka (для аналитики)
        await self._kafka_publisher.publish_task_event(updated_task, event_type)

        await self._cache.delete_task_statistics()

        logger.info(f"Task updated: id={updated_task.id}, event={event_type}")
        return updated_task

    def __escalate(self):

    def __detect_event_type(
            self,
            old_update_task: TaskSchema,
            new_update_task: TaskSchema,
    ):
        return TaskEventType.UPDATED
        if new_update_task.status and old_update_task.status != new_update_task.status:
            return TaskEventType.STATUS_CHANGED
        elif new_update_task.assignee and old_update_task.assignee != new_update_task.assignee:
            return TaskEventType.ASSIGNED
        elif not old_update_task.assignee and not old_update_task.status and not old_update_task.priority:
            return TaskEventType.PRIORITY_ESCALATED