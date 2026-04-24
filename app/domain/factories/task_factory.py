"""TaskFactory — створює Task з перевіркою інваріантів."""
from datetime import datetime, timezone
from typing import Optional

from app.domain.errors import (
    DomainError, AssigneeNotFoundError, DueDateInPastError,
)
from app.domain.models.task import Task, TaskPriority
from app.domain.repositories.user_repository import IUserRepository


class TaskFactory:
    def __init__(self, user_repo: IUserRepository):
        self._user_repo = user_repo

    def create(
        self,
        title: str,
        project_id: int,
        priority: TaskPriority = TaskPriority.MEDIUM,
        description: Optional[str] = None,
        due_date: Optional[datetime] = None,
        assignee_id: Optional[int] = None,
    ) -> Task:
        title = title.strip()
        if not title:
            raise DomainError("Task title cannot be empty")
        if len(title) > 256:
            raise DomainError("Task title must not exceed 256 characters")

        # Простий інваріант: дата в майбутньому
        if due_date is not None:
            if due_date.tzinfo is None:
                due_date = due_date.replace(tzinfo=timezone.utc)
            if due_date <= datetime.now(timezone.utc):
                raise DueDateInPastError()

        # Складний інваріант: assignee існує
        if assignee_id is not None:
            if not self._user_repo.get_by_id(assignee_id):
                raise AssigneeNotFoundError(assignee_id)

        return Task(
            title=title,
            project_id=project_id,
            priority=priority,
            description=description,
            due_date=due_date,
            assignee_id=assignee_id,
        )
