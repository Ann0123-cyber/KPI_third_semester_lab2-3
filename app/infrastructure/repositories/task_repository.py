"""SQLAlchemy реалізація ITaskRepository."""
from sqlalchemy.orm import Session

from app.domain.models.task import Task
from app.domain.repositories.task_repository import ITaskRepository
from app.infrastructure.mappers.task_mapper import TaskMapper
from app.infrastructure.orm.task_orm import TaskORM, TaskStatusORM, TaskPriorityORM


class SqlTaskRepository(ITaskRepository):
    def __init__(self, db: Session):
        self._db = db

    def get_by_id(self, task_id: int) -> Task | None:
        orm = self._db.query(TaskORM).filter(TaskORM.id == task_id).first()
        return TaskMapper.to_domain(orm) if orm else None

    def get_by_project(self, project_id: int) -> list[Task]:
        orms = self._db.query(TaskORM).filter(TaskORM.project_id == project_id).all()
        return [TaskMapper.to_domain(o) for o in orms]

    def save(self, task: Task) -> Task:
        if task.id is None:
            orm = TaskMapper.to_orm(task)
            self._db.add(orm)
            self._db.commit()
            self._db.refresh(orm)
            return TaskMapper.to_domain(orm)
        else:
            orm = self._db.query(TaskORM).filter(TaskORM.id == task.id).first()
            orm.title = task.title
            orm.description = task.description
            orm.status = TaskStatusORM(task.status.value)
            orm.priority = TaskPriorityORM(task.priority.value)
            orm.due_date = task.due_date
            orm.assignee_id = task.assignee_id
            self._db.commit()
            self._db.refresh(orm)
            return TaskMapper.to_domain(orm)

    def delete(self, task_id: int) -> None:
        orm = self._db.query(TaskORM).filter(TaskORM.id == task_id).first()
        if orm:
            self._db.delete(orm)
            self._db.commit()
