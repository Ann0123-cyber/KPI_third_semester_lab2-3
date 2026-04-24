"""Mapper: TaskORM ↔ Task domain model."""
from app.domain.models.task import Task, TaskStatus, TaskPriority
from app.infrastructure.orm.task_orm import TaskORM, TaskStatusORM, TaskPriorityORM


class TaskMapper:
    @staticmethod
    def to_domain(orm: TaskORM) -> Task:
        return Task(
            id=orm.id,
            title=orm.title,
            description=orm.description,
            status=TaskStatus(orm.status.value),
            priority=TaskPriority(orm.priority.value),
            due_date=orm.due_date,
            project_id=orm.project_id,
            assignee_id=orm.assignee_id,
            created_at=orm.created_at,
        )

    @staticmethod
    def to_orm(domain: Task) -> TaskORM:
        orm = TaskORM(
            title=domain.title,
            description=domain.description,
            status=TaskStatusORM(domain.status.value),
            priority=TaskPriorityORM(domain.priority.value),
            due_date=domain.due_date,
            project_id=domain.project_id,
            assignee_id=domain.assignee_id,
        )
        if domain.id is not None:
            orm.id = domain.id
        return orm
