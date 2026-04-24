"""Інтерфейс репозиторію User — визначений у домені (DIP)."""
from abc import ABC, abstractmethod
from app.domain.models.user import User


class IUserRepository(ABC):
    @abstractmethod
    def get_by_id(self, user_id: int) -> User | None: ...

    @abstractmethod
    def get_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    def get_by_username(self, username: str) -> User | None: ...

    @abstractmethod
    def save(self, user: User) -> User: ...
