from app.application.commands.tasks.create_task_command import CreateTaskCommand
from app.domain.errors import ProjectNotFoundError
from app.domain.factories.task_factory import TaskFactory
from app.domain.repositories.project_repository import IProjectRepository
from app.domain.repositories.task_repository import ITaskRepository
from app.domain.repositories.user_repository import IUserRepository


class CreateTaskHandler:
    def __init__(self, task_repo: ITaskRepository, project_repo: IProjectRepository, user_repo: IUserRepository):
        self._task_repo = task_repo
        self._project_repo = project_repo
        self._factory = TaskFactory(user_repo)

    def handle(self, cmd: CreateTaskCommand) -> int:
        """Повертає лише ID створеної задачі."""
        project = self._project_repo.get_by_id(cmd.project_id)
        if not project or project.owner_id != cmd.owner_id:
            raise ProjectNotFoundError(cmd.project_id)

        task = self._factory.create(
            title=cmd.title,
            project_id=cmd.project_id,
            priority=cmd.priority,
            description=cmd.description,
            due_date=cmd.due_date,
            assignee_id=cmd.assignee_id,
        )
        saved = self._task_repo.save(task)
        return saved.id
