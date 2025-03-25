from fastapi import APIRouter, HTTPException, Depends
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

@router.get("/")
async def get_tasks(current_user: CurrentUser = Depends(get_current_user)):
    try:
        tasks = await get_tasks_service()
        return {"tasks": tasks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{user_id}")
async def get_user_tasks(user_id: int, current_user: CurrentUser = Depends(get_current_user)):
    try:
        tasks = await get_user_tasks_service(user_id)
        return {"tasks": tasks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_task(task: TaskCreate, current_user: CurrentUser = Depends(get_current_user)):
    try:
        result = await create_task_service(task, current_user.id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{task_id}")
async def get_task(task_id: int, current_user: CurrentUser = Depends(get_current_user)):
    try:
        task = await get_task_service(task_id)
        if "message" in task:
            raise HTTPException(status_code=404, detail=task["message"])
        return task
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{task_id}")
async def update_task(task_id: int, task: TaskCreate, current_user: CurrentUser = Depends(get_current_user)):
    try:
        result = await update_task_service(task_id, task, current_user.id)
        if "message" in result and "permission" in result["message"].lower():
            raise HTTPException(status_code=403, detail=result["message"])
        if "message" in result and "not found" in result["message"].lower():
            raise HTTPException(status_code=404, detail=result["message"])
        return result
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{task_id}")
async def delete_task(task_id: int, current_user: CurrentUser = Depends(get_current_user)):
    try:
        result = await delete_task_service(task_id, current_user.id)
        if "message" in result and "permission" in result["message"].lower():
            raise HTTPException(status_code=403, detail=result["message"])
        if "message" in result and "not found" in result["message"].lower():
            raise HTTPException(status_code=404, detail=result["message"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


