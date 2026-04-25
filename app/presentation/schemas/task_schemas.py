from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, field_validator
from app.domain.models.task import TaskStatus, TaskPriority

class CreateTaskRequest(BaseModel):
    title: str
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None
    assignee_id: Optional[int] = None

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Task title cannot be empty")
        if len(v) > 256:
            raise ValueError("Task title must not exceed 256 characters")
        return v.strip()

    @field_validator("due_date")
    @classmethod
    def due_date_future(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v is not None:
            if v.tzinfo is None:
                v = v.replace(tzinfo=timezone.utc)
            if v <= datetime.now(timezone.utc):
                raise ValueError("Due date must be in the future")
        return v

class UpdateTaskRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    assignee_id: Optional[int] = None
    status: Optional[TaskStatus] = None

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    due_date: Optional[datetime]
    project_id: int
    assignee_id: Optional[int]
    created_at: datetime
