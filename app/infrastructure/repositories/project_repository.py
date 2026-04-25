"""SQLAlchemy реалізація IProjectRepository."""
from sqlalchemy.orm import Session

from app.domain.models.project import Project
from app.domain.repositories.project_repository import IProjectRepository
from app.infrastructure.mappers.project_mapper import ProjectMapper
from app.infrastructure.orm.project_orm import ProjectORM


class SqlProjectRepository(IProjectRepository):
    def __init__(self, db: Session):
        self._db = db

    def get_by_id(self, project_id: int) -> Project | None:
        orm = self._db.query(ProjectORM).filter(ProjectORM.id == project_id).first()
        return ProjectMapper.to_domain(orm) if orm else None

    def get_by_owner(self, owner_id: int) -> list[Project]:
        orms = self._db.query(ProjectORM).filter(ProjectORM.owner_id == owner_id).all()
        return [ProjectMapper.to_domain(o) for o in orms]

    def get_by_name_and_owner(self, name: str, owner_id: int) -> Project | None:
        orm = self._db.query(ProjectORM).filter(
            ProjectORM.name == name, ProjectORM.owner_id == owner_id
        ).first()
        return ProjectMapper.to_domain(orm) if orm else None

    def save(self, project: Project) -> Project:
        if project.id is None:
            orm = ProjectMapper.to_orm(project)
            self._db.add(orm)
            self._db.commit()
            self._db.refresh(orm)
            return ProjectMapper.to_domain(orm)
        else:
            orm = self._db.query(ProjectORM).filter(ProjectORM.id == project.id).first()
            orm.name = project.name
            orm.description = project.description
            self._db.commit()
            self._db.refresh(orm)
            return ProjectMapper.to_domain(orm)

    def delete(self, project_id: int) -> None:
        orm = self._db.query(ProjectORM).filter(ProjectORM.id == project_id).first()
        if orm:
            self._db.delete(orm)
            self._db.commit()
