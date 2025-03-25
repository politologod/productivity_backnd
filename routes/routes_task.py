from fastapi import APIRouter
from models.model_task import TaskCreate
from services.service_task import get_tasks as get_tasks_service
from services.service_task import create_task as create_task_service
from services.service_task import get_task as get_task_service
from services.service_task import update_task as update_task_service
from services.service_task import delete_task as delete_task_service

router = APIRouter(prefix="/tasks", tags=["Tasks"])






@router.get("/")
async def get_tasks():
    return await get_tasks_service()

@router.post("/")
async def create_task(task: TaskCreate):
    return await create_task_service(task)

@router.get("/{task_id}")
async def get_task(task_id: int):
    return await get_task_service(task_id)

@router.put("/{task_id}")
async def update_task(task_id: int, task: TaskCreate):
    return await update_task_service(task_id, task)

@router.delete("/{task_id}")
async def delete_task(task_id: int):
    return await delete_task_service(task_id)


