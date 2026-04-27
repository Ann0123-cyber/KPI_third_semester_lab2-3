from dataclasses import dataclass

@dataclass(frozen=True)
class ListProjectsQuery:
    owner_id: int
