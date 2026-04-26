"""
Fake in-memory реалізації інтерфейсів репозиторіїв.
Використовуються в unit-тестах — жодного SQLAlchemy, жодної БД.
"""
from app.domain.models.user import User
from app.domain.models.project import Project
from app.domain.models.task import Task
from app.domain.repositories.user_repository import IUserRepository
from app.domain.repositories.project_repository import IProjectRepository
from app.domain.repositories.task_repository import ITaskRepository


class FakeUserRepository(IUserRepository):
    def __init__(self):
        self._store: dict[int, User] = {}
        self._next_id = 1

    def get_by_id(self, user_id: int) -> User | None:
        return self._store.get(user_id)

    def get_by_email(self, email: str) -> User | None:
        return next((u for u in self._store.values() if str(u.email) == email), None)

    def get_by_username(self, username: str) -> User | None:
        return next((u for u in self._store.values() if str(u.username) == username), None)

    def save(self, user: User) -> User:
        if user.id is None:
            user.id = self._next_id
            self._next_id += 1
        self._store[user.id] = user
        return user


class FakeProjectRepository(IProjectRepository):
    def __init__(self):
        self._store: dict[int, Project] = {}
        self._next_id = 1

    def get_by_id(self, project_id: int) -> Project | None:
        return self._store.get(project_id)

    def get_by_owner(self, owner_id: int) -> list[Project]:
        return [p for p in self._store.values() if p.owner_id == owner_id]

    def get_by_name_and_owner(self, name: str, owner_id: int) -> Project | None:
        return next((p for p in self._store.values()
                     if p.name == name and p.owner_id == owner_id), None)

    def save(self, project: Project) -> Project:
        if project.id is None:
            project.id = self._next_id
            self._next_id += 1
        self._store[project.id] = project
        return project

    def delete(self, project_id: int) -> None:
        self._store.pop(project_id, None)


class FakeTaskRepository(ITaskRepository):
    def __init__(self):
        self._store: dict[int, Task] = {}
        self._next_id = 1

    def get_by_id(self, task_id: int) -> Task | None:
        return self._store.get(task_id)

    def get_by_project(self, project_id: int) -> list[Task]:
        return [t for t in self._store.values() if t.project_id == project_id]

    def save(self, task: Task) -> Task:
        if task.id is None:
            task.id = self._next_id
            self._next_id += 1
        self._store[task.id] = task
        return task

    def delete(self, task_id: int) -> None:
        self._store.pop(task_id, None)
