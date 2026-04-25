"""SQLAlchemy реалізація IUserRepository."""
from sqlalchemy.orm import Session

from app.domain.models.user import User
from app.domain.repositories.user_repository import IUserRepository
from app.infrastructure.mappers.user_mapper import UserMapper
from app.infrastructure.orm.user_orm import UserORM


class SqlUserRepository(IUserRepository):
    def __init__(self, db: Session):
        self._db = db

    def get_by_id(self, user_id: int) -> User | None:
        orm = self._db.query(UserORM).filter(UserORM.id == user_id).first()
        return UserMapper.to_domain(orm) if orm else None

    def get_by_email(self, email: str) -> User | None:
        orm = self._db.query(UserORM).filter(UserORM.email == email).first()
        return UserMapper.to_domain(orm) if orm else None

    def get_by_username(self, username: str) -> User | None:
        orm = self._db.query(UserORM).filter(UserORM.username == username).first()
        return UserMapper.to_domain(orm) if orm else None

    def save(self, user: User) -> User:
        if user.id is None:
            orm = UserMapper.to_orm(user)
            self._db.add(orm)
            self._db.commit()
            self._db.refresh(orm)
            return UserMapper.to_domain(orm)
        else:
            orm = self._db.query(UserORM).filter(UserORM.id == user.id).first()
            orm.email = str(user.email)
            orm.username = str(user.username)
            orm.hashed_password = user.hashed_password
            self._db.commit()
            self._db.refresh(orm)
            return UserMapper.to_domain(orm)
