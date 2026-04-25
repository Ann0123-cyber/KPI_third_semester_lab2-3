from fastapi import APIRouter, Depends, status
from app.application.use_cases.projects.create_project import CreateProjectUseCase, CreateProjectCommand
from app.application.use_cases.projects.list_projects import ListProjectsUseCase
from app.application.use_cases.projects.get_project import GetProjectUseCase
from app.application.use_cases.projects.update_project import UpdateProjectUseCase, UpdateProjectCommand
from app.application.use_cases.projects.delete_project import DeleteProjectUseCase, DeleteProjectCommand
from app.domain.models.user import User
from app.infrastructure.repositories.project_repository import SqlProjectRepository
from app.presentation.dependencies import get_project_repo, get_current_user
from app.presentation.schemas.project_schemas import CreateProjectRequest, UpdateProjectRequest, ProjectResponse

router = APIRouter(prefix="/projects", tags=["projects"])


def _resp(p) -> ProjectResponse:
    return ProjectResponse(id=p.id, name=p.name, description=p.description, owner_id=p.owner_id, created_at=p.created_at)


@router.get("/", response_model=list[ProjectResponse])
def list_projects(repo: SqlProjectRepository = Depends(get_project_repo), user: User = Depends(get_current_user)):
    return [_resp(p) for p in ListProjectsUseCase(repo).execute(user.id)]


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(req: CreateProjectRequest, repo: SqlProjectRepository = Depends(get_project_repo), user: User = Depends(get_current_user)):
    return _resp(CreateProjectUseCase(repo).execute(CreateProjectCommand(name=req.name, owner_id=user.id, description=req.description)))


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, repo: SqlProjectRepository = Depends(get_project_repo), user: User = Depends(get_current_user)):
    return _resp(GetProjectUseCase(repo).execute(project_id, user.id))


@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, req: UpdateProjectRequest, repo: SqlProjectRepository = Depends(get_project_repo), user: User = Depends(get_current_user)):
    return _resp(UpdateProjectUseCase(repo).execute(UpdateProjectCommand(project_id=project_id, owner_id=user.id, name=req.name, description=req.description)))


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, repo: SqlProjectRepository = Depends(get_project_repo), user: User = Depends(get_current_user)):
    DeleteProjectUseCase(repo).execute(DeleteProjectCommand(project_id=project_id, owner_id=user.id))
