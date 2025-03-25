from fastapi import APIRouter, Depends, HTTPException
from database.database import get_database
from services.statistics_service import StatisticsService
from services.service_auth import get_current_user
from models.model_user import User
from models.model_statistics import UserStatistics
from bson import ObjectId

router = APIRouter(
    prefix="/statistics",
    tags=["statistics"]
)

@router.get("/user/{user_id}", response_model=UserStatistics)
async def get_user_statistics(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    # Solo permitir que los usuarios vean sus propias estadísticas o que los admins vean todas
    if str(current_user.id) != user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="No tienes permiso para ver estas estadísticas"
        )
    
    statistics = await StatisticsService.calculate_user_statistics(user_id)
    return statistics

@router.get("/all", response_model=list[UserStatistics])
async def get_all_statistics(
    current_user: User = Depends(get_current_user)
):
    # Solo los admins pueden ver todas las estadísticas
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Solo los administradores pueden ver todas las estadísticas"
        )
    
    # Obtener todos los usuarios
    db = await get_database()
    users = await db.users.find().to_list(None)
    statistics = [await StatisticsService.calculate_user_statistics(str(user["_id"])) for user in users]
    return statistics 