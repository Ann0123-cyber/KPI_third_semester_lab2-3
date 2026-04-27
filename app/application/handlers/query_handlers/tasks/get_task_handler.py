from sqlalchemy.orm import Session

from app.application.queries.tasks.get_task_query import GetTaskQuery
from app.application.read_models.task_read_model import TaskReadModel
from app.domain.errors import ProjectNotFoundError, TaskNotFoundError
from app.domain.models.task import TaskStatus, TaskPriority
from app.infrastructure.orm.project_orm import ProjectORM
from app.infrastructure.orm.task_orm import TaskORM
from app.infrastructure.orm.user_orm import UserORM


class GetTaskHandler:
    def __init__(self, db: Session):
        self._db = db

    def handle(self, query: GetTaskQuery) -> TaskReadModel:
        project = self._db.query(ProjectORM).filter(
            ProjectORM.id == query.project_id,
            ProjectORM.owner_id == query.owner_id,
        ).first()
        if not project:
            raise ProjectNotFoundError(query.project_id)

        result = (
            self._db.query(TaskORM, UserORM.username)
            .outerjoin(UserORM, UserORM.id == TaskORM.assignee_id)
            .filter(TaskORM.id == query.task_id, TaskORM.project_id == query.project_id)
            .first()
        )
        if not result:
            raise TaskNotFoundError(query.task_id)

        t, username = result
        return TaskReadModel(
            id=t.id,
            title=t.title,
            description=t.description,
            status=TaskStatus(t.status.value),
            priority=TaskPriority(t.priority.value),
            due_date=t.due_date,
            project_id=t.project_id,
            assignee_id=t.assignee_id,
            assignee_username=username,
            created_at=t.created_at,
        )
