from fastapi import APIRouter, HTTPException, Depends, status
from models.model_task import Task, TaskCreate
from models.model_auth import CurrentUser
from services.service_task import (
    get_tasks as get_tasks_service,
    get_user_tasks as get_user_tasks_service,
    create_task as create_task_service,
    update_task as update_task_service,
    delete_task as delete_task_service,
    move_task as move_task_service
)
from services.service_auth import get_current_user

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
    responses={404: {"description": "No encontrado"}}
)

@router.get(
    "",
    response_model=list[Task],
    status_code=status.HTTP_200_OK,
    summary="Obtener todas las tareas",
    description="Obtiene todas las tareas según el rol del usuario",
    responses={
        200: {
            "description": "Lista de tareas obtenida exitosamente",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "title": "Tarea ejemplo",
                            "description": "Descripción de la tarea",
                            "due_date": "2024-03-31T23:59:59",
                            "priority": "alta",
                            "status": "en_progreso",
                            "column_id": 1,
                            "created_by": 1,
                            "assigned_to": 2,
                            "created_at": "2024-03-15T10:00:00",
                            "updated_at": "2024-03-15T10:00:00"
                        }
                    ]
                }
            }
        }
    }
)
async def get_tasks(current_user: CurrentUser = Depends(get_current_user)):
    try:
        tasks = await get_tasks_service(current_user.id, current_user.role)
        return tasks
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get(
    "/user/{user_id}",
    response_model=list[Task],
    status_code=status.HTTP_200_OK,
    summary="Obtener tareas de un usuario",
    description="Obtiene todas las tareas asignadas a un usuario específico",
    responses={
        200: {
            "description": "Lista de tareas del usuario obtenida exitosamente",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "title": "Tarea ejemplo",
                            "description": "Descripción de la tarea",
                            "due_date": "2024-03-31T23:59:59",
                            "priority": "alta",
                            "status": "en_progreso",
                            "column_id": 1,
                            "created_by": 1,
                            "assigned_to": 2,
                            "created_at": "2024-03-15T10:00:00",
                            "updated_at": "2024-03-15T10:00:00"
                        }
                    ]
                }
            }
        }
    }
)
async def get_user_tasks(user_id: int, current_user: CurrentUser = Depends(get_current_user)):
    try:
        tasks = await get_user_tasks_service(user_id, current_user.id, current_user.role)
        return tasks
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post(
    "",
    response_model=Task,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva tarea",
    description="Crea una nueva tarea en el sistema",
    responses={
        201: {
            "description": "Tarea creada exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "title": "Tarea ejemplo",
                        "description": "Descripción de la tarea",
                        "due_date": "2024-03-31T23:59:59",
                        "priority": "alta",
                        "status": "en_progreso",
                        "column_id": 1,
                        "created_by": 1,
                        "assigned_to": 2,
                        "created_at": "2024-03-15T10:00:00",
                        "updated_at": "2024-03-15T10:00:00"
                    }
                }
            }
        }
    }
)
async def create_task(task: TaskCreate, current_user: CurrentUser = Depends(get_current_user)):
    try:
        result = await create_task_service(task, current_user.id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put(
    "/{task_id}",
    response_model=Task,
    status_code=status.HTTP_200_OK,
    summary="Actualizar una tarea",
    description="Actualiza una tarea existente en el sistema",
    responses={
        200: {
            "description": "Tarea actualizada exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "title": "Tarea ejemplo",
                        "description": "Descripción de la tarea",
                        "due_date": "2024-03-31T23:59:59",
                        "priority": "alta",
                        "status": "en_progreso",
                        "column_id": 1,
                        "created_by": 1,
                        "assigned_to": 2,
                        "created_at": "2024-03-15T10:00:00",
                        "updated_at": "2024-03-15T10:00:00"
                    }
                }
            }
        }
    }
)
async def update_task(
    task_id: int,
    task: TaskCreate,
    current_user: CurrentUser = Depends(get_current_user)
):
    try:
        result = await update_task_service(task_id, task, current_user.id, current_user.role)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete(
    "/{task_id}",
    status_code=status.HTTP_200_OK,
    summary="Eliminar una tarea",
    description="Elimina una tarea del sistema",
    responses={
        200: {
            "description": "Tarea eliminada exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Task deleted successfully"
                    }
                }
            }
        }
    }
)
async def delete_task(task_id: int, current_user: CurrentUser = Depends(get_current_user)):
    try:
        result = await delete_task_service(task_id, current_user.id, current_user.role)
        return {"message": "Task deleted successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post(
    "/{task_id}/move",
    response_model=Task,
    status_code=status.HTTP_200_OK,
    summary="Mover una tarea a otra columna",
    description="Mueve una tarea a una columna diferente en el tablero Kanban",
    responses={
        200: {
            "description": "Tarea movida exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "title": "Tarea ejemplo",
                        "description": "Descripción de la tarea",
                        "due_date": "2024-03-31T23:59:59",
                        "priority": "alta",
                        "status": "en_progreso",
                        "column_id": 2,
                        "created_by": 1,
                        "assigned_to": 2,
                        "created_at": "2024-03-15T10:00:00",
                        "updated_at": "2024-03-15T10:00:00"
                    }
                }
            }
        }
    }
)
async def move_task(
    task_id: int,
    new_column_id: int,
    current_user: CurrentUser = Depends(get_current_user)
):
    try:
        result = await move_task_service(task_id, new_column_id, current_user.id, current_user.role)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


