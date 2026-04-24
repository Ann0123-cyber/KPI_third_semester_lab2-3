"""
Task — Rich Domain Model.
Містить поведінку (transition_to) — логіка переходів живе в домені, не в сервісах.
"""
from __future__ import annotations

import enum
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from app.domain.errors import InvalidStatusTransitionError


class TaskStatus(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"


class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


_ALLOWED_TRANSITIONS: dict[TaskStatus, set[TaskStatus]] = {
    TaskStatus.TODO:        {TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED},
    TaskStatus.IN_PROGRESS: {TaskStatus.DONE, TaskStatus.TODO, TaskStatus.CANCELLED},
    TaskStatus.DONE:        {TaskStatus.TODO},
    TaskStatus.CANCELLED:   {TaskStatus.TODO},
}


@dataclass
class Task:
    title: str
    project_id: int
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    assignee_id: Optional[int] = None
    id: Optional[int] = field(default=None)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # ── Rich Domain Behaviour ─────────────────────────────────────────────────

    def transition_to(self, new_status: TaskStatus) -> None:
        """Перевіряє та застосовує перехід статусу. Інваріант живе тут."""
        allowed = _ALLOWED_TRANSITIONS.get(self.status, set())
        if new_status not in allowed:
            raise InvalidStatusTransitionError(
                from_status=self.status.value,
                to_status=new_status.value,
                allowed=[s.value for s in allowed],
            )
        self.status = new_status

    def assign_to(self, user_id: int) -> None:
        self.assignee_id = user_id

    def update_details(
        self,
        title: str | None = None,
        description: str | None = None,
        priority: TaskPriority | None = None,
        due_date: datetime | None = None,
    ) -> None:
        if title is not None:
            self.title = title
        if description is not None:
            self.description = description
        if priority is not None:
            self.priority = priority
        if due_date is not None:
            self.due_date = due_date

    @classmethod
    def allowed_transitions(cls) -> dict[TaskStatus, set[TaskStatus]]:
        return _ALLOWED_TRANSITIONS
