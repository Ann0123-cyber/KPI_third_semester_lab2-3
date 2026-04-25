from app.domain.errors import ProjectNotFoundError
from app.domain.models.project import Project
from app.domain.repositories.project_repository import IProjectRepository

class GetProjectUseCase:
    def __init__(self, project_repo: IProjectRepository):
        self._repo = project_repo

    def execute(self, project_id: int, owner_id: int) -> Project:
        project = self._repo.get_by_id(project_id)
        if not project or project.owner_id != owner_id:
            raise ProjectNotFoundError(project_id)
        return project
