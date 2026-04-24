"""Mapper: UserORM ↔ User domain model. Живе в Infrastructure."""
from app.domain.models.user import User
from app.domain.value_objects.email import Email
from app.domain.value_objects.username import Username
from app.infrastructure.orm.user_orm import UserORM


class UserMapper:
    @staticmethod
    def to_domain(orm: UserORM) -> User:
        return User(
            id=orm.id,
            email=Email(orm.email),
            username=Username(orm.username),
            hashed_password=orm.hashed_password,
            created_at=orm.created_at,
        )

    @staticmethod
    def to_orm(domain: User) -> UserORM:
        orm = UserORM(
            email=str(domain.email),
            username=str(domain.username),
            hashed_password=domain.hashed_password,
        )
        if domain.id is not None:
            orm.id = domain.id
        return orm
