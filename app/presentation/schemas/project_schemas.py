from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator

class CreateProjectRequest(BaseModel):
    name: str
    description: Optional[str] = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Project name cannot be empty")
        if len(v) > 128:
            raise ValueError("Project name must not exceed 128 characters")
        return v.strip()

class UpdateProjectRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    owner_id: int
    created_at: datetime
    task_count: int = 0
