from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class UpdateProjectCommand:
    project_id: int
    owner_id: int
    name: Optional[str] = None
    description: Optional[str] = None
