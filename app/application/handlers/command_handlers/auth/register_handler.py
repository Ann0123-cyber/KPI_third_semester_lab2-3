from app.application.commands.auth.register_command import RegisterUserCommand
from app.application.read_models.user_read_model import UserReadModel
from app.domain.factories.user_factory import UserFactory
from app.domain.repositories.user_repository import IUserRepository


class RegisterUserHandler:
    def __init__(self, user_repo: IUserRepository, password_hasher):
        self._factory = UserFactory(user_repo, password_hasher)
        self._repo = user_repo

    def handle(self, cmd: RegisterUserCommand) -> UserReadModel:
        """Виняток з правила — реєстрація повертає дані нового юзера."""
        user = self._factory.create(cmd.email, cmd.username, cmd.password)
        saved = self._repo.save(user)
        return UserReadModel(
            id=saved.id,
            email=str(saved.email),
            username=str(saved.username),
            created_at=saved.created_at,
        )
