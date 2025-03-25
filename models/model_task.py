from pydantic import BaseModel, field_validator
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

    @field_validator('title')
    @classmethod
    def title_length(cls, v):
        if len(v) < 3:
            raise ValueError('El título debe tener al menos 3 caracteres')
        if len(v) > 100:
            raise ValueError('El título no puede exceder los 100 caracteres')
        return v.strip()

    @field_validator('description')
    @classmethod
    def description_length(cls, v):
        if len(v) < 10:
            raise ValueError('La descripción debe tener al menos 10 caracteres')
        if len(v) > 1000:
            raise ValueError('La descripción no puede exceder los 1000 caracteres')
        return v.strip()

    @field_validator('assigned_to')
    @classmethod
    def validate_assigned_users(cls, v):
        if not v:
            raise ValueError('La tarea debe tener al menos un usuario asignado')
        if len(v) > 10:
            raise ValueError('No se pueden asignar más de 10 usuarios a una tarea')
        return v

    @field_validator('due_date')
    @classmethod
    def validate_due_date(cls, v):
        if v < datetime.now():
            raise ValueError('La fecha de vencimiento no puede ser en el pasado')
        return v


class Task(TaskCreate):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None  # ID del usuario que creó la tarea

    class Config:
        from_attributes = True


