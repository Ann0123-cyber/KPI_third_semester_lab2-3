from sqlalchemy.orm import Session

from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate


def get_project(db: Session, project_id: int, owner_id: int) -> Project:
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == owner_id,
    ).first()
    if not project:
        raise LookupError(f"Project {project_id} not found")
    return project


def list_projects(db: Session, owner_id: int) -> list[Project]:
    return db.query(Project).filter(Project.owner_id == owner_id).all()


def create_project(db: Session, data: ProjectCreate, owner_id: int) -> Project:
    existing = db.query(Project).filter(
        Project.name == data.name,
        Project.owner_id == owner_id,
    ).first()
    if existing:
        raise ValueError(f"You already have a project named '{data.name}'")

    project = Project(name=data.name, description=data.description, owner_id=owner_id)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def update_project(db: Session, project_id: int, data: ProjectUpdate, owner_id: int) -> Project:
    project = get_project(db, project_id, owner_id)

    if data.name is not None and data.name != project.name:
        conflict = db.query(Project).filter(
            Project.name == data.name,
            Project.owner_id == owner_id,
            Project.id != project_id,
        ).first()
        if conflict:
            raise ValueError(f"You already have a project named '{data.name}'")
        project.name = data.name

    if data.description is not None:
        project.description = data.description

    db.commit()
    db.refresh(project)
    return project


def delete_project(db: Session, project_id: int, owner_id: int) -> None:
    project = get_project(db, project_id, owner_id)
    db.delete(project)
    db.commit()
