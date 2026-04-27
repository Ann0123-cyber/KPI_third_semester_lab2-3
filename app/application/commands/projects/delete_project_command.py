from dataclasses import dataclass

@dataclass(frozen=True)
class DeleteProjectCommand:
    project_id: int
    owner_id: int
