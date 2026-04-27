from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from app.domain.models.task import TaskStatus, TaskPriority


@dataclass(frozen=True)
class TaskReadModel:
    id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    due_date: Optional[datetime]
    project_id: int
    assignee_id: Optional[int]
    assignee_username: Optional[str]  # денормалізовано — UI не робить додаткового запиту
    created_at: datetime
