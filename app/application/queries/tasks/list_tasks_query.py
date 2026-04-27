from dataclasses import dataclass

@dataclass(frozen=True)
class ListTasksQuery:
    project_id: int
    owner_id: int
