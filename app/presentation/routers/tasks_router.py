from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.application.commands.tasks.create_task_command import CreateTaskCommand
from app.application.commands.tasks.update_task_command import UpdateTaskCommand
from app.application.commands.tasks.delete_task_command import DeleteTaskCommand
from app.application.queries.tasks.list_tasks_query import ListTasksQuery
from app.application.queries.tasks.get_task_query import GetTaskQuery

from app.application.handlers.command_handlers.tasks.create_task_handler import CreateTaskHandler
from app.application.handlers.command_handlers.tasks.update_task_handler import UpdateTaskHandler
from app.application.handlers.command_handlers.tasks.delete_task_handler import DeleteTaskHandler
from app.application.handlers.query_handlers.tasks.list_tasks_handler import ListTasksHandler
from app.application.handlers.query_handlers.tasks.get_task_handler import GetTaskHandler

from app.domain.models.user import User
from app.infrastructure.database import get_db
from app.infrastructure.repositories.project_repository import SqlProjectRepository
from app.infrastructure.repositories.task_repository import SqlTaskRepository
from app.infrastructure.repositories.user_repository import SqlUserRepository
from app.presentation.dependencies import get_current_user
from app.presentation.schemas.task_schemas import CreateTaskRequest, UpdateTaskRequest, TaskResponse

router = APIRouter(prefix="/projects/{project_id}/tasks", tags=["tasks"])


def _rm_to_response(rm) -> TaskResponse:
    return TaskResponse(id=rm.id, title=rm.title, description=rm.description,
                        status=rm.status, priority=rm.priority, due_date=rm.due_date,
                        project_id=rm.project_id, assignee_id=rm.assignee_id,
                        assignee_username=rm.assignee_username, created_at=rm.created_at)


@router.get("/", response_model=list[TaskResponse])
def list_tasks(project_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return [_rm_to_response(rm) for rm in ListTasksHandler(db).handle(ListTasksQuery(project_id=project_id, owner_id=user.id))]


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(project_id: int, req: CreateTaskRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    cmd = CreateTaskCommand(title=req.title, project_id=project_id, owner_id=user.id,
                            priority=req.priority, description=req.description,
                            due_date=req.due_date, assignee_id=req.assignee_id)
    task_id = CreateTaskHandler(SqlTaskRepository(db), SqlProjectRepository(db), SqlUserRepository(db)).handle(cmd)
    return _rm_to_response(GetTaskHandler(db).handle(GetTaskQuery(project_id=project_id, task_id=task_id, owner_id=user.id)))


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(project_id: int, task_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return _rm_to_response(GetTaskHandler(db).handle(GetTaskQuery(project_id=project_id, task_id=task_id, owner_id=user.id)))


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(project_id: int, task_id: int, req: UpdateTaskRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    cmd = UpdateTaskCommand(project_id=project_id, task_id=task_id, owner_id=user.id,
                            title=req.title, description=req.description, priority=req.priority,
                            due_date=req.due_date, assignee_id=req.assignee_id, status=req.status)
    UpdateTaskHandler(SqlTaskRepository(db), SqlProjectRepository(db), SqlUserRepository(db)).handle(cmd)
    return _rm_to_response(GetTaskHandler(db).handle(GetTaskQuery(project_id=project_id, task_id=task_id, owner_id=user.id)))


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(project_id: int, task_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    DeleteTaskHandler(SqlTaskRepository(db), SqlProjectRepository(db)).handle(
        DeleteTaskCommand(project_id=project_id, task_id=task_id, owner_id=user.id))
