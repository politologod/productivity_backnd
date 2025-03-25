from datetime import datetime, timedelta
from database.database import get_database
from models.model_user import User
from models.model_task import Task
from models.model_statistics import UserStatistics
from bson import ObjectId

class StatisticsService:
    @staticmethod
    async def calculate_user_statistics(user_id: str) -> UserStatistics:
        db = await get_database()
        
        # Obtener todas las tareas del usuario
        tasks = await db.tasks.find({"user_id": ObjectId(user_id)}).to_list(None)
        
        # Calcular estadísticas básicas
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t["status"] == "completada"])
        pending_tasks = total_tasks - completed_tasks
        
        # Calcular tiempo promedio de completado
        completed_tasks_with_time = [
            t for t in tasks 
            if t["status"] == "completada" and t.get("completed_at") and t.get("created_at")
        ]
        if completed_tasks_with_time:
            total_time = sum(
                (t["completed_at"] - t["created_at"]).total_seconds() 
                for t in completed_tasks_with_time
            )
            average_completion_time = total_time / len(completed_tasks_with_time) / 3600  # convertir a horas
        else:
            average_completion_time = 0.0
        
        # Calcular tareas por prioridad
        tasks_by_priority = {
            "alta": len([t for t in tasks if t["priority"] == "alta"]),
            "media": len([t for t in tasks if t["priority"] == "media"]),
            "baja": len([t for t in tasks if t["priority"] == "baja"])
        }
        
        # Calcular tareas por estado
        tasks_by_status = {
            "completada": len([t for t in tasks if t["status"] == "completada"]),
            "en_progreso": len([t for t in tasks if t["status"] == "en_progreso"]),
            "pendiente": len([t for t in tasks if t["status"] == "pendiente"])
        }
        
        # Calcular última actividad
        last_activity = max((t["updated_at"] for t in tasks), default=datetime.now())
        
        # Calcular racha de días
        today = datetime.now().date()
        streak_days = 0
        current_date = today
        while True:
            has_activity = any(t["updated_at"].date() == current_date for t in tasks)
            if not has_activity:
                break
            streak_days += 1
            current_date -= timedelta(days=1)
        
        # Calcular puntuación de productividad (0-100)
        if total_tasks > 0:
            completion_rate = completed_tasks / total_tasks
            priority_score = (tasks_by_priority["alta"] * 0.5 + tasks_by_priority["media"] * 0.3 + tasks_by_priority["baja"] * 0.2) / total_tasks
            productivity_score = (completion_rate * 0.6 + priority_score * 0.4) * 100
        else:
            productivity_score = 0.0
        
        return UserStatistics(
            user_id=user_id,
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            pending_tasks=pending_tasks,
            average_completion_time=average_completion_time,
            tasks_by_priority=tasks_by_priority,
            tasks_by_status=tasks_by_status,
            last_activity=last_activity,
            streak_days=streak_days,
            productivity_score=productivity_score
        ) 