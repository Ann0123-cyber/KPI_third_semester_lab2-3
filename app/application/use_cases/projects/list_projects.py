from app.domain.models.project import Project
from app.domain.repositories.project_repository import IProjectRepository

class ListProjectsUseCase:
    def __init__(self, project_repo: IProjectRepository):
        self._repo = project_repo

    def execute(self, owner_id: int) -> list[Project]:
        return self._repo.get_by_owner(owner_id)
