from dataclasses import dataclass

@dataclass(frozen=True)
class GetProjectQuery:
    project_id: int
    owner_id: int
