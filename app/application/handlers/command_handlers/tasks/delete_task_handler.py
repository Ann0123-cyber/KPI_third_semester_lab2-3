from app.application.commands.tasks.delete_task_command import DeleteTaskCommand
from app.domain.errors import ProjectNotFoundError, TaskNotFoundError
from app.domain.repositories.project_repository import IProjectRepository
from app.domain.repositories.task_repository import ITaskRepository


class DeleteTaskHandler:
    def __init__(self, task_repo: ITaskRepository, project_repo: IProjectRepository):
        self._task_repo = task_repo
        self._project_repo = project_repo

    def handle(self, cmd: DeleteTaskCommand) -> None:
        project = self._project_repo.get_by_id(cmd.project_id)
        if not project or project.owner_id != cmd.owner_id:
            raise ProjectNotFoundError(cmd.project_id)
        task = self._task_repo.get_by_id(cmd.task_id)
        if not task or task.project_id != cmd.project_id:
            raise TaskNotFoundError(cmd.task_id)
        self._task_repo.delete(cmd.task_id)
