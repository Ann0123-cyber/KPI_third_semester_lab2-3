from app.application.commands.auth.login_command import LoginCommand
from app.domain.errors import InvalidCredentialsError
from app.domain.repositories.user_repository import IUserRepository


class LoginHandler:
    def __init__(self, user_repo: IUserRepository, password_verifier, token_creator):
        self._repo = user_repo
        self._verify = password_verifier
        self._create_token = token_creator

    def handle(self, cmd: LoginCommand) -> str:
        """Повертає токен — виняток з правила (не стан системи)."""
        user = self._repo.get_by_email(cmd.email)
        if not user or not self._verify(cmd.password, user.hashed_password):
            raise InvalidCredentialsError()
        return self._create_token(user.id)
