from sqlalchemy.orm import Session
from sqlalchemy import func

from app.application.queries.projects.get_project_query import GetProjectQuery
from app.application.read_models.project_read_model import ProjectReadModel
from app.domain.errors import ProjectNotFoundError
from app.infrastructure.orm.project_orm import ProjectORM
from app.infrastructure.orm.task_orm import TaskORM


class GetProjectHandler:
    def __init__(self, db: Session):
        self._db = db

    def handle(self, query: GetProjectQuery) -> ProjectReadModel:
        result = (
            self._db.query(
                ProjectORM,
                func.count(TaskORM.id).label("task_count"),
            )
            .outerjoin(TaskORM, TaskORM.project_id == ProjectORM.id)
            .filter(ProjectORM.id == query.project_id, ProjectORM.owner_id == query.owner_id)
            .group_by(ProjectORM.id)
            .first()
        )

        if not result:
            raise ProjectNotFoundError(query.project_id)

        p, task_count = result
        return ProjectReadModel(
            id=p.id,
            name=p.name,
            description=p.description,
            owner_id=p.owner_id,
            created_at=p.created_at,
            task_count=task_count,
        )
