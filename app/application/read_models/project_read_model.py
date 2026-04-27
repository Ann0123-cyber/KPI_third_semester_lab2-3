"""
Read Models — DTO оптимізовані під потреби клієнта.
Не є доменними моделями. Повертаються Query Handlers.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class ProjectReadModel:
    id: int
    name: str
    description: Optional[str]
    owner_id: int
    created_at: datetime
    task_count: int = 0  # денормалізоване поле — зручне для UI, відсутнє в доменній моделі
