from dataclasses import dataclass
from app.domain.factories.project_factory import ProjectFactory
from app.domain.models.project import Project
from app.domain.repositories.project_repository import IProjectRepository

@dataclass
class CreateProjectCommand:
    name: str
    owner_id: int
    description: str | None = None

class CreateProjectUseCase:
    def __init__(self, project_repo: IProjectRepository):
        self._factory = ProjectFactory(project_repo)
        self._repo = project_repo

    def execute(self, cmd: CreateProjectCommand) -> Project:
        project = self._factory.create(cmd.name, cmd.owner_id, cmd.description)
        return self._repo.save(project)
