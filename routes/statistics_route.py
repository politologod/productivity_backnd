from fastapi import APIRouter, Depends, HTTPException, status
from database.database import get_database
from services.statistics_service import StatisticsService
from services.service_auth import get_current_user
from models.model_user import User
from models.model_statistics import UserStatistics
from bson import ObjectId
from typing import List

router = APIRouter(
    prefix="/statistics",
    tags=["statistics"],
    responses={404: {"description": "No encontrado"}},
)

@router.get(
    "/user/{user_id}",
    response_model=UserStatistics,
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "description": "Estadísticas obtenidas exitosamente",
            "content": {
                "application/json": {
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
            }
        },
        403: {"description": "No tienes permiso para ver estas estadísticas"},
        404: {"description": "Usuario no encontrado"}
    }
)
async def get_user_statistics(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    # Solo permitir que los usuarios vean sus propias estadísticas o que los admins vean todas
    if str(current_user.id) != user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver estas estadísticas"
        )
    
    statistics = await StatisticsService.calculate_user_statistics(user_id)
    return statistics

@router.get(
    "/all",
    response_model=List[UserStatistics],
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "description": "Lista de estadísticas obtenida exitosamente",
            "content": {
                "application/json": {
                    "example": [
                        {
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
                    ]
                }
            }
        },
        403: {"description": "Solo los administradores pueden ver todas las estadísticas"}
    }
)
async def get_all_statistics(
    current_user: User = Depends(get_current_user)
):
    # Solo los admins pueden ver todas las estadísticas
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden ver todas las estadísticas"
        )
    
    # Obtener todos los usuarios
    db = await get_database()
    users = await db.users.find().to_list(None)
    statistics = [await StatisticsService.calculate_user_statistics(str(user["_id"])) for user in users]
    return statistics 