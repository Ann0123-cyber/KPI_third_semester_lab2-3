from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from app.domain.errors import ProjectNotFoundError, TaskNotFoundError, AssigneeNotFoundError
from app.domain.models.task import Task, TaskStatus, TaskPriority
from app.domain.repositories.project_repository import IProjectRepository
from app.domain.repositories.task_repository import ITaskRepository
from app.domain.repositories.user_repository import IUserRepository

@dataclass
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

class UpdateTaskUseCase:
    def __init__(self, task_repo: ITaskRepository, project_repo: IProjectRepository, user_repo: IUserRepository):
        self._task_repo = task_repo
        self._project_repo = project_repo
        self._user_repo = user_repo

    def execute(self, cmd: UpdateTaskCommand) -> Task:
        project = self._project_repo.get_by_id(cmd.project_id)
        if not project or project.owner_id != cmd.owner_id:
            raise ProjectNotFoundError(cmd.project_id)

        task = self._task_repo.get_by_id(cmd.task_id)
        if not task or task.project_id != cmd.project_id:
            raise TaskNotFoundError(cmd.task_id)

        # Rich domain model — логіка переходу живе в Task.transition_to()
        if cmd.status is not None and cmd.status != task.status:
            task.transition_to(cmd.status)  # кидає InvalidStatusTransitionError якщо недопустимо

        if cmd.assignee_id is not None:
            if not self._user_repo.get_by_id(cmd.assignee_id):
                raise AssigneeNotFoundError(cmd.assignee_id)
            task.assign_to(cmd.assignee_id)

        task.update_details(
            title=cmd.title,
            description=cmd.description,
            priority=cmd.priority,
            due_date=cmd.due_date,
        )
        return self._task_repo.save(task)
