"""Інтерфейс репозиторію Project."""
from abc import ABC, abstractmethod
from app.domain.models.project import Project


class IProjectRepository(ABC):
    @abstractmethod
    def get_by_id(self, project_id: int) -> Project | None: ...

    @abstractmethod
    def get_by_owner(self, owner_id: int) -> list[Project]: ...

    @abstractmethod
    def get_by_name_and_owner(self, name: str, owner_id: int) -> Project | None: ...

    @abstractmethod
    def save(self, project: Project) -> Project: ...

    @abstractmethod
    def delete(self, project_id: int) -> None: ...
