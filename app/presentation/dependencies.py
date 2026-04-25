"""DI: створення use cases з реальними залежностями."""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.infrastructure.repositories.user_repository import SqlUserRepository
from app.infrastructure.repositories.project_repository import SqlProjectRepository
from app.infrastructure.repositories.task_repository import SqlTaskRepository
from app.infrastructure.auth.password_service import hash_password, verify_password
from app.infrastructure.auth.jwt_service import create_token, decode_token
from app.domain.models.user import User

bearer = HTTPBearer()


def get_user_repo(db: Session = Depends(get_db)) -> SqlUserRepository:
    return SqlUserRepository(db)

def get_project_repo(db: Session = Depends(get_db)) -> SqlProjectRepository:
    return SqlProjectRepository(db)

def get_task_repo(db: Session = Depends(get_db)) -> SqlTaskRepository:
    return SqlTaskRepository(db)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    user_repo: SqlUserRepository = Depends(get_user_repo),
) -> User:
    try:
        user_id = decode_token(credentials.credentials)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    user = user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
