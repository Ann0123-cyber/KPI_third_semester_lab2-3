from app.application.commands.tasks.update_task_command import UpdateTaskCommand
from app.domain.errors import ProjectNotFoundError, TaskNotFoundError, AssigneeNotFoundError
from app.domain.repositories.project_repository import IProjectRepository
from app.domain.repositories.task_repository import ITaskRepository
from app.domain.repositories.user_repository import IUserRepository


class UpdateTaskHandler:
    def __init__(self, task_repo: ITaskRepository, project_repo: IProjectRepository, user_repo: IUserRepository):
        self._task_repo = task_repo
        self._project_repo = project_repo
        self._user_repo = user_repo

    def handle(self, cmd: UpdateTaskCommand) -> None:
        project = self._project_repo.get_by_id(cmd.project_id)
        if not project or project.owner_id != cmd.owner_id:
            raise ProjectNotFoundError(cmd.project_id)

        task = self._task_repo.get_by_id(cmd.task_id)
        if not task or task.project_id != cmd.project_id:
            raise TaskNotFoundError(cmd.task_id)

        # Rich domain model — логіка переходу в Task.transition_to()
        if cmd.status is not None and cmd.status != task.status:
            task.transition_to(cmd.status)

        if cmd.assignee_id is not None:
            if not self._user_repo.get_by_id(cmd.assignee_id):
                raise AssigneeNotFoundError(cmd.assignee_id)
            task.assign_to(cmd.assignee_id)

        task.update_details(
            title=cmd.title,
            description=cmd.description,
            priority=cmd.priority,
            due_date=cmd.due_date,
        )
        self._task_repo.save(task)
