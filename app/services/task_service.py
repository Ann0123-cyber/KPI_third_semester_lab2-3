from sqlalchemy.orm import Session

from app.models.task import Task, ALLOWED_TRANSITIONS
from app.models.project import Project
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate


def _assert_project_access(db: Session, project_id: int, owner_id: int) -> Project:
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == owner_id,
    ).first()
    if not project:
        raise LookupError(f"Project {project_id} not found")
    return project


def get_task(db: Session, project_id: int, task_id: int, owner_id: int) -> Task:
    _assert_project_access(db, project_id, owner_id)
    task = db.query(Task).filter(Task.id == task_id, Task.project_id == project_id).first()
    if not task:
        raise LookupError(f"Task {task_id} not found in project {project_id}")
    return task


def list_tasks(db: Session, project_id: int, owner_id: int) -> list[Task]:
    _assert_project_access(db, project_id, owner_id)
    return db.query(Task).filter(Task.project_id == project_id).all()


def create_task(db: Session, project_id: int, data: TaskCreate, owner_id: int) -> Task:
    _assert_project_access(db, project_id, owner_id)

    if data.assignee_id is not None:
        assignee = db.query(User).filter(User.id == data.assignee_id).first()
        if not assignee:
            raise LookupError(f"User {data.assignee_id} not found")

    task = Task(
        title=data.title,
        description=data.description,
        priority=data.priority,
        due_date=data.due_date,
        project_id=project_id,
        assignee_id=data.assignee_id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def update_task(db: Session, project_id: int, task_id: int, data: TaskUpdate, owner_id: int) -> Task:
    task = get_task(db, project_id, task_id, owner_id)

    # Invariant: only allowed status transitions
    if data.status is not None and data.status != task.status:
        allowed = ALLOWED_TRANSITIONS.get(task.status, set())
        if data.status not in allowed:
            raise ValueError(
                f"Cannot transition task from '{task.status}' to '{data.status}'. "
                f"Allowed transitions: {[s.value for s in allowed]}"
            )
        task.status = data.status

    if data.title is not None:
        task.title = data.title
    if data.description is not None:
        task.description = data.description
    if data.priority is not None:
        task.priority = data.priority
    if data.due_date is not None:
        task.due_date = data.due_date
    if data.assignee_id is not None:
        assignee = db.query(User).filter(User.id == data.assignee_id).first()
        if not assignee:
            raise LookupError(f"User {data.assignee_id} not found")
        task.assignee_id = data.assignee_id

    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, project_id: int, task_id: int, owner_id: int) -> None:
    task = get_task(db, project_id, task_id, owner_id)
    db.delete(task)
    db.commit()
