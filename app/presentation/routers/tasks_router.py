from fastapi import APIRouter, Depends, status
from app.application.use_cases.tasks.create_task import CreateTaskUseCase, CreateTaskCommand
from app.application.use_cases.tasks.list_tasks import ListTasksUseCase
from app.application.use_cases.tasks.get_task import GetTaskUseCase
from app.application.use_cases.tasks.update_task import UpdateTaskUseCase, UpdateTaskCommand
from app.application.use_cases.tasks.delete_task import DeleteTaskUseCase, DeleteTaskCommand
from app.domain.models.user import User
from app.infrastructure.repositories.project_repository import SqlProjectRepository
from app.infrastructure.repositories.task_repository import SqlTaskRepository
from app.infrastructure.repositories.user_repository import SqlUserRepository
from app.presentation.dependencies import get_project_repo, get_task_repo, get_user_repo, get_current_user
from app.presentation.schemas.task_schemas import CreateTaskRequest, UpdateTaskRequest, TaskResponse

router = APIRouter(prefix="/projects/{project_id}/tasks", tags=["tasks"])


def _resp(t) -> TaskResponse:
    return TaskResponse(id=t.id, title=t.title, description=t.description, status=t.status,
                        priority=t.priority, due_date=t.due_date, project_id=t.project_id,
                        assignee_id=t.assignee_id, created_at=t.created_at)


@router.get("/", response_model=list[TaskResponse])
def list_tasks(project_id: int, task_repo=Depends(get_task_repo), project_repo=Depends(get_project_repo), user: User = Depends(get_current_user)):
    return [_resp(t) for t in ListTasksUseCase(task_repo, project_repo).execute(project_id, user.id)]


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(project_id: int, req: CreateTaskRequest, task_repo=Depends(get_task_repo), project_repo=Depends(get_project_repo), user_repo=Depends(get_user_repo), user: User = Depends(get_current_user)):
    cmd = CreateTaskCommand(title=req.title, project_id=project_id, owner_id=user.id,
                            priority=req.priority, description=req.description,
                            due_date=req.due_date, assignee_id=req.assignee_id)
    return _resp(CreateTaskUseCase(task_repo, project_repo, user_repo).execute(cmd))


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(project_id: int, task_id: int, task_repo=Depends(get_task_repo), project_repo=Depends(get_project_repo), user: User = Depends(get_current_user)):
    return _resp(GetTaskUseCase(task_repo, project_repo).execute(project_id, task_id, user.id))


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(project_id: int, task_id: int, req: UpdateTaskRequest, task_repo=Depends(get_task_repo), project_repo=Depends(get_project_repo), user_repo=Depends(get_user_repo), user: User = Depends(get_current_user)):
    cmd = UpdateTaskCommand(project_id=project_id, task_id=task_id, owner_id=user.id,
                            title=req.title, description=req.description, priority=req.priority,
                            due_date=req.due_date, assignee_id=req.assignee_id, status=req.status)
    return _resp(UpdateTaskUseCase(task_repo, project_repo, user_repo).execute(cmd))


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(project_id: int, task_id: int, task_repo=Depends(get_task_repo), project_repo=Depends(get_project_repo), user: User = Depends(get_current_user)):
    DeleteTaskUseCase(task_repo, project_repo).execute(DeleteTaskCommand(project_id=project_id, task_id=task_id, owner_id=user.id))
