from dataclasses import dataclass

@dataclass(frozen=True)
class GetTaskQuery:
    project_id: int
    task_id: int
    owner_id: int
