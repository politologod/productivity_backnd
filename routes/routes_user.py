from fastapi import APIRouter, HTTPException
from models.model_user import UserCreate
from services.service_user import (
    get_users as get_users_service,
    create_user as create_user_service,
    get_user as get_user_service,
    update_user as update_user_service,
    delete_user as delete_user_service
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/")
async def get_users():
    try:
        users = await get_users_service()
        return {"users": users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/")
async def create_user(user: UserCreate):
    try:
        result = await create_user_service(user)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}")
async def get_user(user_id: int):
    try:
        user = await get_user_service(user_id)
        if "message" in user:
            raise HTTPException(status_code=404, detail=user["message"])
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{user_id}")
async def update_user(user_id: int, user: UserCreate):
    try:
        result = await update_user_service(user_id, user)
        if "message" in result and result["message"] == "Failed to update user":
            raise HTTPException(status_code=404, detail="User not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{user_id}")
async def delete_user(user_id: int):
    try:
        result = await delete_user_service(user_id)
        if result["message"] == "User not found":
            raise HTTPException(status_code=404, detail="User not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))   










