from dataclasses import dataclass
from typing import Optional
from app.domain.errors import ProjectNotFoundError, DuplicateProjectNameError, DomainError
from app.domain.models.project import Project
from app.domain.repositories.project_repository import IProjectRepository

@dataclass
class UpdateProjectCommand:
    project_id: int
    owner_id: int
    name: Optional[str] = None
    description: Optional[str] = None

class UpdateProjectUseCase:
    def __init__(self, project_repo: IProjectRepository):
        self._repo = project_repo

    def execute(self, cmd: UpdateProjectCommand) -> Project:
        project = self._repo.get_by_id(cmd.project_id)
        if not project or project.owner_id != cmd.owner_id:
            raise ProjectNotFoundError(cmd.project_id)

        if cmd.name is not None:
            new_name = cmd.name.strip()
            if not new_name:
                raise DomainError("Project name cannot be empty")
            if new_name != project.name:
                conflict = self._repo.get_by_name_and_owner(new_name, cmd.owner_id)
                if conflict:
                    raise DuplicateProjectNameError(new_name)
            project.name = new_name

        if cmd.description is not None:
            project.description = cmd.description

        return self._repo.save(project)
