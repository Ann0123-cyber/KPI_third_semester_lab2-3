from dataclasses import dataclass
from app.domain.errors import ProjectNotFoundError
from app.domain.repositories.project_repository import IProjectRepository

@dataclass
class DeleteProjectCommand:
    project_id: int
    owner_id: int

class DeleteProjectUseCase:
    def __init__(self, project_repo: IProjectRepository):
        self._repo = project_repo

    def execute(self, cmd: DeleteProjectCommand) -> None:
        project = self._repo.get_by_id(cmd.project_id)
        if not project or project.owner_id != cmd.owner_id:
            raise ProjectNotFoundError(cmd.project_id)
        self._repo.delete(cmd.project_id)
