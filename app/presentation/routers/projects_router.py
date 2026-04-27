"""
Тонкий контролер — лише маппінг HTTP → Command/Query → Handler.
Жодної бізнес-логіки.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.application.commands.projects.create_project_command import CreateProjectCommand
from app.application.commands.projects.update_project_command import UpdateProjectCommand
from app.application.commands.projects.delete_project_command import DeleteProjectCommand
from app.application.queries.projects.list_projects_query import ListProjectsQuery
from app.application.queries.projects.get_project_query import GetProjectQuery

from app.application.handlers.command_handlers.projects.create_project_handler import CreateProjectHandler
from app.application.handlers.command_handlers.projects.update_project_handler import UpdateProjectHandler
from app.application.handlers.command_handlers.projects.delete_project_handler import DeleteProjectHandler
from app.application.handlers.query_handlers.projects.list_projects_handler import ListProjectsHandler
from app.application.handlers.query_handlers.projects.get_project_handler import GetProjectHandler

from app.domain.models.user import User
from app.infrastructure.database import get_db
from app.infrastructure.repositories.project_repository import SqlProjectRepository
from app.presentation.dependencies import get_current_user
from app.presentation.schemas.project_schemas import CreateProjectRequest, UpdateProjectRequest, ProjectResponse

router = APIRouter(prefix="/projects", tags=["projects"])


def _read_model_to_response(rm) -> ProjectResponse:
    return ProjectResponse(id=rm.id, name=rm.name, description=rm.description,
                           owner_id=rm.owner_id, created_at=rm.created_at, task_count=rm.task_count)


@router.get("/", response_model=list[ProjectResponse])
def list_projects(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    query = ListProjectsQuery(owner_id=user.id)
    read_models = ListProjectsHandler(db).handle(query)
    return [_read_model_to_response(rm) for rm in read_models]


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(req: CreateProjectRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    cmd = CreateProjectCommand(name=req.name, owner_id=user.id, description=req.description)
    project_id = CreateProjectHandler(SqlProjectRepository(db)).handle(cmd)
    # після команди — читаємо через Query Handler
    query = GetProjectQuery(project_id=project_id, owner_id=user.id)
    return _read_model_to_response(GetProjectHandler(db).handle(query))


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    query = GetProjectQuery(project_id=project_id, owner_id=user.id)
    return _read_model_to_response(GetProjectHandler(db).handle(query))


@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, req: UpdateProjectRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    cmd = UpdateProjectCommand(project_id=project_id, owner_id=user.id, name=req.name, description=req.description)
    UpdateProjectHandler(SqlProjectRepository(db)).handle(cmd)
    query = GetProjectQuery(project_id=project_id, owner_id=user.id)
    return _read_model_to_response(GetProjectHandler(db).handle(query))


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    cmd = DeleteProjectCommand(project_id=project_id, owner_id=user.id)
    DeleteProjectHandler(SqlProjectRepository(db)).handle(cmd)