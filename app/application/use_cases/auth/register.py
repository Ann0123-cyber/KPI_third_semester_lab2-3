"""UC: Реєстрація користувача."""
from dataclasses import dataclass
from app.domain.factories.user_factory import UserFactory
from app.domain.models.user import User
from app.domain.repositories.user_repository import IUserRepository


@dataclass
class RegisterUserCommand:
    email: str
    username: str
    password: str


class RegisterUserUseCase:
    def __init__(self, user_repo: IUserRepository, password_hasher):
        self._factory = UserFactory(user_repo, password_hasher)
        self._repo = user_repo

    def execute(self, cmd: RegisterUserCommand) -> User:
        user = self._factory.create(cmd.email, cmd.username, cmd.password)
        return self._repo.save(user)
