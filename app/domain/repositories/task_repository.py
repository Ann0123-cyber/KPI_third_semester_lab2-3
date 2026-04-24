"""Інтерфейс репозиторію Task."""
from abc import ABC, abstractmethod
from app.domain.models.task import Task


class ITaskRepository(ABC):
    @abstractmethod
    def get_by_id(self, task_id: int) -> Task | None: ...

    @abstractmethod
    def get_by_project(self, project_id: int) -> list[Task]: ...

    @abstractmethod
    def save(self, task: Task) -> Task: ...

    @abstractmethod
    def delete(self, task_id: int) -> None: ...
