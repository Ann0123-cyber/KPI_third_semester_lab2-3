from app.domain.errors import ProjectNotFoundError
from app.domain.models.task import Task
from app.domain.repositories.project_repository import IProjectRepository
from app.domain.repositories.task_repository import ITaskRepository

class ListTasksUseCase:
    def __init__(self, task_repo: ITaskRepository, project_repo: IProjectRepository):
        self._task_repo = task_repo
        self._project_repo = project_repo

    def execute(self, project_id: int, owner_id: int) -> list[Task]:
        project = self._project_repo.get_by_id(project_id)
        if not project or project.owner_id != owner_id:
            raise ProjectNotFoundError(project_id)
        return self._task_repo.get_by_project(project_id)
