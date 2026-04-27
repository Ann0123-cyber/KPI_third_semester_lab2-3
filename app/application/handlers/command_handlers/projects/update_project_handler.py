from app.application.commands.projects.update_project_command import UpdateProjectCommand
from app.domain.errors import ProjectNotFoundError, DuplicateProjectNameError, DomainError
from app.domain.repositories.project_repository import IProjectRepository


class UpdateProjectHandler:
    def __init__(self, project_repo: IProjectRepository):
        self._repo = project_repo

    def handle(self, cmd: UpdateProjectCommand) -> None:
        project = self._repo.get_by_id(cmd.project_id)
        if not project or project.owner_id != cmd.owner_id:
            raise ProjectNotFoundError(cmd.project_id)

        if cmd.name is not None:
            new_name = cmd.name.strip()
            if not new_name:
                raise DomainError("Project name cannot be empty")
            if new_name != project.name:
                if self._repo.get_by_name_and_owner(new_name, cmd.owner_id):
                    raise DuplicateProjectNameError(new_name)
            project.name = new_name

        if cmd.description is not None:
            project.description = cmd.description

        self._repo.save(project)
