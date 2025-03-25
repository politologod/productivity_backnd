from pydantic import BaseModel
from enum import Enum
from datetime import datetime
from typing import Optional, List


class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class Status(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"


class TaskCreate(BaseModel):
    title: str
    description: str
    priority: Priority
    assigned_to: List[int]  # Lista de IDs de usuarios
    due_date: datetime
    status: Status = Status.pending


class Task(TaskCreate):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None  # ID del usuario que creó la tarea

    class Config:
        from_attributes = True


