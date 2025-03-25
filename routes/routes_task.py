from fastapi import APIRouter, HTTPException, Depends, status
from models.model_task import TaskCreate
from models.model_auth import CurrentUser
from services.service_task import (
    get_tasks as get_tasks_service,
    create_task as create_task_service,
    get_task as get_task_service,
    update_task as update_task_service,
    delete_task as delete_task_service,
    get_user_tasks as get_user_tasks_service
)
from services.service_auth import get_current_user

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.get("/", status_code=status.HTTP_200_OK)
async def get_tasks(current_user: CurrentUser = Depends(get_current_user)):
    try:
        tasks = await get_tasks_service()
        return {"tasks": tasks}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/user/{user_id}", status_code=status.HTTP_200_OK)
async def get_user_tasks(user_id: int, current_user: CurrentUser = Depends(get_current_user)):
    try:
        if current_user.role != "admin" and current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        tasks = await get_user_tasks_service(user_id)
        return {"tasks": tasks}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate, current_user: CurrentUser = Depends(get_current_user)):
    try:
        result = await create_task_service(task, current_user.id)
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

@router.get("/{task_id}", status_code=status.HTTP_200_OK)
async def get_task(task_id: int, current_user: CurrentUser = Depends(get_current_user)):
    try:
        task = await get_task_service(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        return task
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/{task_id}", status_code=status.HTTP_200_OK)
async def update_task(task_id: int, task: TaskCreate, current_user: CurrentUser = Depends(get_current_user)):
    try:
        result = await update_task_service(task_id, task, current_user.id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
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

@router.delete("/{task_id}", status_code=status.HTTP_200_OK)
async def delete_task(task_id: int, current_user: CurrentUser = Depends(get_current_user)):
    try:
        result = await delete_task_service(task_id, current_user.id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


