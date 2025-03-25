from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from services.statistics_service import StatisticsService
from services.auth_service import get_current_user
from models.model_user import User
from models.model_statistics import UserStatistics

router = APIRouter(
    prefix="/statistics",
    tags=["statistics"]
)

@router.get("/user/{user_id}", response_model=UserStatistics)
async def get_user_statistics(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Solo permitir que los usuarios vean sus propias estadísticas o que los admins vean todas
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="No tienes permiso para ver estas estadísticas"
        )
    
    statistics = StatisticsService.calculate_user_statistics(db, user_id)
    return statistics

@router.get("/all", response_model=list[UserStatistics])
async def get_all_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Solo los admins pueden ver todas las estadísticas
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Solo los administradores pueden ver todas las estadísticas"
        )
    
    # Obtener todos los usuarios
    users = db.query(User).all()
    statistics = [StatisticsService.calculate_user_statistics(db, user.id) for user in users]
    return statistics 