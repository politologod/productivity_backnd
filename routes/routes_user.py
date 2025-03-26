from fastapi import APIRouter, HTTPException, Depends, status
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
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin access required."
        )

@router.get("/", status_code=status.HTTP_200_OK)
async def get_users(current_user: CurrentUser = Depends(get_current_user)):
    try:
        # Solo los administradores pueden ver todos los usuarios
        check_admin_access(current_user)
        users = await get_users_service()
        return {"users": users}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, current_user: CurrentUser = Depends(get_current_user)):
    try:
        # Solo los administradores pueden crear usuarios
        check_admin_access(current_user)
        result = await create_user_service(user)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{user_id}", status_code=status.HTTP_200_OK)
async def get_user(
    user_id: int,
    include_tasks: bool = False,
    current_user: CurrentUser = Depends(get_current_user)
):
    try:
        # Solo permitir que los usuarios vean sus propios datos o que los admins vean todos
        if current_user.role != "admin" and current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para ver este usuario"
            )
            
        user = await get_user_service(user_id, include_tasks)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/{user_id}", status_code=status.HTTP_200_OK)
async def update_user(user_id: int, user: UserCreate, current_user: CurrentUser = Depends(get_current_user)):
    try:
        # Los usuarios solo pueden actualizar su propio perfil, los admin pueden actualizar todos
        if current_user.role != "admin" and current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        result = await update_user_service(user_id, user)
        if "message" in result and result["message"] == "Failed to update user":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(user_id: int, current_user: CurrentUser = Depends(get_current_user)):
    try:
        # Solo los administradores pueden eliminar usuarios
        check_admin_access(current_user)
        result = await delete_user_service(user_id)
        if result["message"] == "User not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )   










