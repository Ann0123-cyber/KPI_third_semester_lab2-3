from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from app.domain.errors import ProjectNotFoundError
from app.domain.factories.task_factory import TaskFactory
from app.domain.models.task import Task, TaskPriority
from app.domain.repositories.project_repository import IProjectRepository
from app.domain.repositories.task_repository import ITaskRepository
from app.domain.repositories.user_repository import IUserRepository

@dataclass
class CreateTaskCommand:
    title: str
    project_id: int
    owner_id: int
    priority: TaskPriority = TaskPriority.MEDIUM
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    assignee_id: Optional[int] = None

class CreateTaskUseCase:
    def __init__(self, task_repo: ITaskRepository, project_repo: IProjectRepository, user_repo: IUserRepository):
        self._task_repo = task_repo
        self._project_repo = project_repo
        self._factory = TaskFactory(user_repo)

    def execute(self, cmd: CreateTaskCommand) -> Task:
        project = self._project_repo.get_by_id(cmd.project_id)
        if not project or project.owner_id != cmd.owner_id:
            raise ProjectNotFoundError(cmd.project_id)

        task = self._factory.create(
            title=cmd.title,
            project_id=cmd.project_id,
            priority=cmd.priority,
            description=cmd.description,
            due_date=cmd.due_date,
            assignee_id=cmd.assignee_id,
        )
        return self._task_repo.save(task)
