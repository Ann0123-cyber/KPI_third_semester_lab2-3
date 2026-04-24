"""User — доменна модель. Не залежить від ORM."""
from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.domain.value_objects.email import Email
from app.domain.value_objects.username import Username


@dataclass
class User:
    email: Email
    username: Username
    hashed_password: str
    id: int | None = field(default=None)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
