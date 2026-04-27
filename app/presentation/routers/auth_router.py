from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.application.commands.auth.register_command import RegisterUserCommand
from app.application.commands.auth.login_command import LoginCommand
from app.application.handlers.command_handlers.auth.register_handler import RegisterUserHandler
from app.application.handlers.command_handlers.auth.login_handler import LoginHandler
from app.infrastructure.auth.password_service import hash_password, verify_password
from app.infrastructure.auth.jwt_service import create_token, decode_token
from app.infrastructure.database import get_db
from app.infrastructure.repositories.user_repository import SqlUserRepository
from app.presentation.dependencies import get_current_user
from app.presentation.schemas.user_schemas import RegisterRequest, LoginRequest, UserResponse, TokenResponse
from app.domain.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


def _get_user_repo(db: Session = Depends(get_db)) -> SqlUserRepository:
    return SqlUserRepository(db)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(req: RegisterRequest, user_repo=Depends(_get_user_repo)):
    # Controller: HTTP → Command → Handler
    cmd = RegisterUserCommand(email=req.email, username=req.username, password=req.password)
    read_model = RegisterUserHandler(user_repo, hash_password).handle(cmd)
    return UserResponse(id=read_model.id, email=read_model.email, username=read_model.username, created_at=read_model.created_at)


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, user_repo=Depends(_get_user_repo)):
    cmd = LoginCommand(email=req.email, password=req.password)
    token = LoginHandler(user_repo, verify_password, create_token).handle(cmd)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return UserResponse(id=current_user.id, email=str(current_user.email),
                        username=str(current_user.username), created_at=current_user.created_at)

