from pydantic import BaseModel, field_validator, Field
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


class TaskBase(BaseModel):
    title: str = Field(..., description="Título de la tarea")
    description: Optional[str] = Field(None, description="Descripción de la tarea")
    due_date: Optional[datetime] = Field(None, description="Fecha de vencimiento de la tarea")
    priority: Optional[str] = Field(None, description="Prioridad de la tarea")
    status: Optional[str] = Field(None, description="Estado de la tarea")
    column_id: Optional[int] = Field(None, description="ID de la columna del Kanban donde se encuentra la tarea")


class TaskCreate(TaskBase):
    assigned_to: Optional[int] = Field(None, description="ID del usuario asignado a la tarea")

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


class Task(TaskBase):
    id: int = Field(..., description="ID único de la tarea")
    created_by: int = Field(..., description="ID del usuario que creó la tarea")
    assigned_to: Optional[int] = Field(None, description="ID del usuario asignado a la tarea")
    created_at: datetime = Field(..., description="Fecha de creación de la tarea")
    updated_at: datetime = Field(..., description="Fecha de última actualización de la tarea")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "Completar informe",
                "description": "Finalizar el informe mensual de ventas",
                "due_date": "2024-03-31T23:59:59",
                "priority": "alta",
                "status": "en_progreso",
                "column_id": 2,
                "created_by": 1,
                "assigned_to": 2,
                "created_at": "2024-03-15T10:00:00",
                "updated_at": "2024-03-15T10:00:00"
            }
        }


