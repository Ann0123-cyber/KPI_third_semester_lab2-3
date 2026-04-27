from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class CreateProjectCommand:
    name: str
    owner_id: int
    description: Optional[str] = None
