from fastapi import APIRouter, HTTPException, Depends
from models.model_user import UserCreate
from models.model_auth import CurrentUser
from services.service_user import (
    get_users as get_users_service,
    create_user as create_user_service,
    get_user as get_user_service,
    update_user as update_user_service,
    delete_user as delete_user_service
)
from services.service_auth import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

def check_admin_access(current_user: CurrentUser):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions. Admin access required."
        )

@router.get("/")
async def get_users(current_user: CurrentUser = Depends(get_current_user)):
    try:
        # Solo los administradores pueden ver todos los usuarios
        check_admin_access(current_user)
        users = await get_users_service()
        return {"users": users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_user(user: UserCreate, current_user: CurrentUser = Depends(get_current_user)):
    try:
        # Solo los administradores pueden crear usuarios
        check_admin_access(current_user)
        result = await create_user_service(user)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}")
async def get_user(user_id: int, current_user: CurrentUser = Depends(get_current_user)):
    try:
        # Los usuarios solo pueden ver su propio perfil, los admin pueden ver todos
        if current_user.role != "admin" and current_user.id != user_id:
            raise HTTPException(
                status_code=403,
                detail="Not enough permissions"
            )
        user = await get_user_service(user_id)
        if "message" in user:
            raise HTTPException(status_code=404, detail=user["message"])
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{user_id}")
async def update_user(user_id: int, user: UserCreate, current_user: CurrentUser = Depends(get_current_user)):
    try:
        # Los usuarios solo pueden actualizar su propio perfil, los admin pueden actualizar todos
        if current_user.role != "admin" and current_user.id != user_id:
            raise HTTPException(
                status_code=403,
                detail="Not enough permissions"
            )
        result = await update_user_service(user_id, user)
        if "message" in result and result["message"] == "Failed to update user":
            raise HTTPException(status_code=404, detail="User not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{user_id}")
async def delete_user(user_id: int, current_user: CurrentUser = Depends(get_current_user)):
    try:
        # Solo los administradores pueden eliminar usuarios
        check_admin_access(current_user)
        result = await delete_user_service(user_id)
        if result["message"] == "User not found":
            raise HTTPException(status_code=404, detail="User not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))   










