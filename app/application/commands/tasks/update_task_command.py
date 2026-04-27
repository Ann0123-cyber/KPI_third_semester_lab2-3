from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from app.domain.models.task import TaskStatus, TaskPriority

@dataclass(frozen=True)
class UpdateTaskCommand:
    project_id: int
    task_id: int
    owner_id: int
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    assignee_id: Optional[int] = None
    status: Optional[TaskStatus] = None
