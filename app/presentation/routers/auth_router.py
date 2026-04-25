from fastapi import APIRouter, Depends, status
from app.application.use_cases.auth.register import RegisterUserUseCase, RegisterUserCommand
from app.application.use_cases.auth.login import LoginUseCase, LoginCommand
from app.infrastructure.auth.password_service import hash_password, verify_password
from app.infrastructure.auth.jwt_service import create_token
from app.infrastructure.repositories.user_repository import SqlUserRepository
from app.presentation.dependencies import get_user_repo, get_current_user
from app.presentation.schemas.user_schemas import RegisterRequest, LoginRequest, UserResponse, TokenResponse
from app.domain.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


def _user_response(user: User) -> UserResponse:
    return UserResponse(id=user.id, email=str(user.email), username=str(user.username), created_at=user.created_at)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(req: RegisterRequest, user_repo: SqlUserRepository = Depends(get_user_repo)):
    uc = RegisterUserUseCase(user_repo, hash_password)
    user = uc.execute(RegisterUserCommand(email=req.email, username=req.username, password=req.password))
    return _user_response(user)


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, user_repo: SqlUserRepository = Depends(get_user_repo)):
    uc = LoginUseCase(user_repo, verify_password, create_token)
    token = uc.execute(LoginCommand(email=req.email, password=req.password))
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return _user_response(current_user)
