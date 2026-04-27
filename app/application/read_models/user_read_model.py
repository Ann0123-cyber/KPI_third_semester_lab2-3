from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class UserReadModel:
    id: int
    email: str
    username: str
    created_at: datetime
