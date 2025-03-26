from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime

class UserStatistics(BaseModel):
    user_id: str = Field(..., description="ID del usuario")
    total_tasks: int = Field(..., description="Número total de tareas del usuario")
    completed_tasks: int = Field(..., description="Número de tareas completadas")
    pending_tasks: int = Field(..., description="Número de tareas pendientes")
    average_completion_time: float = Field(..., description="Tiempo promedio de completado de tareas en horas")
    tasks_by_priority: Dict[str, int] = Field(..., description="Distribución de tareas por prioridad (alta/media/baja)")
    tasks_by_status: Dict[str, int] = Field(..., description="Distribución de tareas por estado (completada/en_progreso/pendiente)")
    last_activity: datetime = Field(..., description="Fecha y hora de la última actividad del usuario")
    streak_days: int = Field(..., description="Número de días consecutivos con actividad")
    productivity_score: float = Field(..., description="Puntuación de productividad del usuario (0-100)")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "user_id": "507f1f77bcf86cd799439011",
                "total_tasks": 15,
                "completed_tasks": 10,
                "pending_tasks": 5,
                "average_completion_time": 2.5,
                "tasks_by_priority": {
                    "alta": 5,
                    "media": 7,
                    "baja": 3
                },
                "tasks_by_status": {
                    "completada": 10,
                    "en_progreso": 3,
                    "pendiente": 2
                },
                "last_activity": "2024-03-20T15:30:00",
                "streak_days": 7,
                "productivity_score": 85.5
            }
        } 