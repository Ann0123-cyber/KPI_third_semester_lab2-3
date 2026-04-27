from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from app.domain.models.task import TaskPriority

@dataclass(frozen=True)
class CreateTaskCommand:
    title: str
    project_id: int
    owner_id: int
    priority: TaskPriority = TaskPriority.MEDIUM
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    assignee_id: Optional[int] = None
