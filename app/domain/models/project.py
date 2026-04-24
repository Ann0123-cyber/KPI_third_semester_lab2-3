"""Project — доменна модель."""
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Project:
    name: str
    owner_id: int
    description: str | None = None
    id: int | None = field(default=None)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
