from arq.cron import cron

@cron("0 9 * * *")
async def escalate_old_pending_tasks(ctx):
    """
    Находит задачи, находящиеся в статусе "pending" более 3 дней,
    и повышает их приоритет.
    low -> medium
    medium -> high
    """
    # Здесь будет ваша бизнес-логика:
    # 1. Подключиться к базе данных.
    # 2. Найти задачи, которые находятся в статусе "pending" более 3 дней.
    # 3. Для каждой такой задачи:
    #    - Повысить приоритет (low -> medium, medium -> high).
    #    - Сохранить изменения в базе данных.
    #    - Опубликовать событие `task.priority_escalated` в Kafka.
    #    - Отправить уведомление assignee.
    print("Запуск задачи escalate_old_pending_tasks...")
    # Примерная логика (вам нужно будет адаптировать ее под ваш проект)
    # db = ctx.get("db") # Получение доступа к БД, если он настроен в worker'е
    # tasks = await db.query(...)
    # for task in tasks:
    #     ...
