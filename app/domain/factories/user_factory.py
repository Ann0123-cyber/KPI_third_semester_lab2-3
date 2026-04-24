"""
UserFactory — створює доменний об'єкт User.
Прості інваріанти: формат email/username, довжина пароля.
Складні інваріанти: унікальність — перевіряються через інтерфейс репозиторію (DIP).
"""
from app.domain.errors import EmailAlreadyExistsError, UsernameAlreadyExistsError
from app.domain.models.user import User
from app.domain.repositories.user_repository import IUserRepository
from app.domain.value_objects.email import Email
from app.domain.value_objects.username import Username


class UserFactory:
    def __init__(self, user_repo: IUserRepository, password_hasher):
        self._repo = user_repo
        self._hasher = password_hasher  # callable: (plain) -> hashed

    def create(self, email: str, username: str, password: str) -> User:
        # Value Objects перевіряють формат (кидають DomainError якщо невалідно)
        email_vo = Email(email)
        username_vo = Username(username)

        if len(password) < 8:
            from app.domain.errors import DomainError
            raise DomainError("Password must be at least 8 characters")

        # Складні інваріанти — через репозиторій
        if self._repo.get_by_email(email):
            raise EmailAlreadyExistsError(email)
        if self._repo.get_by_username(username):
            raise UsernameAlreadyExistsError(username)

        hashed = self._hasher(password)
        return User(email=email_vo, username=username_vo, hashed_password=hashed)
