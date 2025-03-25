from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserStatistics(BaseModel):
    user_id: int
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    average_completion_time: float  # en horas
    tasks_by_priority: dict  # {"alta": 5, "media": 3, "baja": 2}
    tasks_by_status: dict    # {"completada": 10, "en_progreso": 3, "pendiente": 2}
    last_activity: datetime
    streak_days: int        # días consecutivos con actividad
    productivity_score: float  # 0-100
    class Config:
        from_attributes = True 