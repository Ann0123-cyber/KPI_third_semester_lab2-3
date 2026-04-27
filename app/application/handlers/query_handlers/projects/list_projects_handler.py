"""
Query Handler — читає напряму з БД через SQLAlchemy, минаючи доменний шар.
Повертає Read Model (ProjectReadModel), не доменну модель.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.application.queries.projects.list_projects_query import ListProjectsQuery
from app.application.read_models.project_read_model import ProjectReadModel
from app.infrastructure.orm.project_orm import ProjectORM
from app.infrastructure.orm.task_orm import TaskORM


class ListProjectsHandler:
    def __init__(self, db: Session):
        self._db = db

    def handle(self, query: ListProjectsQuery) -> list[ProjectReadModel]:
        # Читаємо напряму з БД — join з підрахунком задач (денормалізація для UI)
        results = (
            self._db.query(
                ProjectORM,
                func.count(TaskORM.id).label("task_count"),
            )
            .outerjoin(TaskORM, TaskORM.project_id == ProjectORM.id)
            .filter(ProjectORM.owner_id == query.owner_id)
            .group_by(ProjectORM.id)
            .all()
        )

        return [
            ProjectReadModel(
                id=p.id,
                name=p.name,
                description=p.description,
                owner_id=p.owner_id,
                created_at=p.created_at,
                task_count=task_count,
            )
            for p, task_count in results
        ]
