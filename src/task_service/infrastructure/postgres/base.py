from sqlalchemy.orm import DeclarativeBase

from task_service.core.config import settings


class Base(DeclarativeBase):
    pass


Base.metadata.schema = settings.POSTGRES_SCHEMA
