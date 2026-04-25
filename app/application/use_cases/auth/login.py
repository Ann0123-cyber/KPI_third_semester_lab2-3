"""UC: Вхід користувача."""
from dataclasses import dataclass
from app.domain.errors import InvalidCredentialsError
from app.domain.repositories.user_repository import IUserRepository


@dataclass
class LoginCommand:
    email: str
    password: str


class LoginUseCase:
    def __init__(self, user_repo: IUserRepository, password_verifier, token_creator):
        self._repo = user_repo
        self._verify = password_verifier   # (plain, hashed) -> bool
        self._create_token = token_creator # (user_id) -> str

    def execute(self, cmd: LoginCommand) -> str:
        user = self._repo.get_by_email(cmd.email)
        if not user or not self._verify(cmd.password, user.hashed_password):
            raise InvalidCredentialsError()
        return self._create_token(user.id)
