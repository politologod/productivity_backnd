from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from models.model_task import Task

class KanbanColumn(BaseModel):
    id: int = Field(..., description="ID único de la columna")
    title: str = Field(..., description="Título de la columna")
    order: int = Field(..., description="Orden de la columna en el tablero")
    created_at: datetime = Field(default_factory=datetime.now, description="Fecha de creación")
    updated_at: datetime = Field(default_factory=datetime.now, description="Fecha de última actualización")
    tasks: Optional[List[Task]] = Field(default=[], description="Lista de tareas en la columna")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "Por Hacer",
                "order": 1,
                "created_at": "2024-03-20T10:00:00",
                "updated_at": "2024-03-20T10:00:00",
                "tasks": []
            }
        }

class KanbanColumnCreate(BaseModel):
    title: str = Field(..., description="Título de la columna")
    order: int = Field(..., description="Orden de la columna en el tablero")

    class Config:
        from_attributes = True 