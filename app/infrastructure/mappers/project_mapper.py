"""Mapper: ProjectORM ↔ Project domain model."""
from app.domain.models.project import Project
from app.infrastructure.orm.project_orm import ProjectORM


class ProjectMapper:
    @staticmethod
    def to_domain(orm: ProjectORM) -> Project:
        return Project(
            id=orm.id,
            name=orm.name,
            description=orm.description,
            owner_id=orm.owner_id,
            created_at=orm.created_at,
        )

    @staticmethod
    def to_orm(domain: Project) -> ProjectORM:
        orm = ProjectORM(
            name=domain.name,
            description=domain.description,
            owner_id=domain.owner_id,
        )
        if domain.id is not None:
            orm.id = domain.id
        return orm
