from app.application.commands.projects.create_project_command import CreateProjectCommand
from app.domain.factories.project_factory import ProjectFactory
from app.domain.repositories.project_repository import IProjectRepository


class CreateProjectHandler:
    def __init__(self, project_repo: IProjectRepository):
        self._factory = ProjectFactory(project_repo)
        self._repo = project_repo

    def handle(self, cmd: CreateProjectCommand) -> int:
        """Повертає лише ID створеного проекту."""
        project = self._factory.create(cmd.name, cmd.owner_id, cmd.description)
        saved = self._repo.save(project)
        return saved.id
