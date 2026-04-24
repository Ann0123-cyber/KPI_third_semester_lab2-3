"""ProjectFactory — створює Project з перевіркою інваріантів."""
from app.domain.errors import DomainError, DuplicateProjectNameError
from app.domain.models.project import Project
from app.domain.repositories.project_repository import IProjectRepository


class ProjectFactory:
    def __init__(self, project_repo: IProjectRepository):
        self._repo = project_repo

    def create(self, name: str, owner_id: int, description: str | None = None) -> Project:
        name = name.strip()
        if not name:
            raise DomainError("Project name cannot be empty")
        if len(name) > 128:
            raise DomainError("Project name must not exceed 128 characters")

        # Складний інваріант: унікальність назви для цього власника
        if self._repo.get_by_name_and_owner(name, owner_id):
            raise DuplicateProjectNameError(name)

        return Project(name=name, owner_id=owner_id, description=description)
