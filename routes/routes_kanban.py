from fastapi import APIRouter, HTTPException, Depends, status
from models.model_kanban import KanbanColumn, KanbanColumnCreate
from models.model_auth import CurrentUser
from services.service_kanban import (
    get_columns as get_columns_service,
    create_column as create_column_service,
    update_column as update_column_service,
    delete_column as delete_column_service,
    move_task as move_task_service
)
from services.service_auth import get_current_user

router = APIRouter(
    prefix="/kanban",
    tags=["Kanban"],
    responses={404: {"description": "No encontrado"}}
)

@router.get(
    "/columns",
    response_model=list[KanbanColumn],
    status_code=status.HTTP_200_OK,
    summary="Obtener todas las columnas",
    description="Obtiene todas las columnas del tablero Kanban con sus tareas",
    responses={
        200: {
            "description": "Lista de columnas obtenida exitosamente",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "title": "Por Hacer",
                            "order": 1,
                            "tasks": [
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
                            ],
                            "created_at": "2024-03-15T10:00:00",
                            "updated_at": "2024-03-15T10:00:00"
                        }
                    ]
                }
            }
        }
    }
)
async def get_columns(current_user: CurrentUser = Depends(get_current_user)):
    try:
        columns = await get_columns_service()
        return columns
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post(
    "/columns",
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva columna",
    description="Crea una nueva columna en el tablero Kanban",
    responses={
        201: {
            "description": "Columna creada exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "column": {
                            "id": 1,
                            "title": "Por Hacer",
                            "order": 1,
                            "tasks": []
                        },
                        "message": "Column created successfully"
                    }
                }
            }
        }
    }
)
async def create_column(column: KanbanColumnCreate, current_user: CurrentUser = Depends(get_current_user)):
    try:
        # Solo los administradores pueden crear columnas
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo los administradores pueden crear columnas"
            )
        result = await create_column_service(column)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put(
    "/columns/{column_id}",
    status_code=status.HTTP_200_OK,
    summary="Actualizar una columna",
    description="Actualiza una columna existente en el tablero Kanban",
    responses={
        200: {
            "description": "Columna actualizada exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "column": {
                            "id": 1,
                            "title": "Por Hacer",
                            "order": 1,
                            "tasks": []
                        },
                        "message": "Column updated successfully"
                    }
                }
            }
        }
    }
)
async def update_column(
    column_id: int,
    column: KanbanColumnCreate,
    current_user: CurrentUser = Depends(get_current_user)
):
    try:
        # Solo los administradores pueden actualizar columnas
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo los administradores pueden actualizar columnas"
            )
        result = await update_column_service(column_id, column)
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
    "/columns/{column_id}",
    status_code=status.HTTP_200_OK,
    summary="Eliminar una columna",
    description="Elimina una columna del tablero Kanban. No se puede eliminar si contiene tareas.",
    responses={
        200: {
            "description": "Columna eliminada exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Column deleted successfully"
                    }
                }
            }
        }
    }
)
async def delete_column(column_id: int, current_user: CurrentUser = Depends(get_current_user)):
    try:
        # Solo los administradores pueden eliminar columnas
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo los administradores pueden eliminar columnas"
            )
        result = await delete_column_service(column_id)
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

@router.post(
    "/tasks/{task_id}/move",
    status_code=status.HTTP_200_OK,
    summary="Mover una tarea a otra columna",
    description="Mueve una tarea a una columna diferente en el tablero Kanban",
    responses={
        200: {
            "description": "Tarea movida exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "task": {
                            "id": 1,
                            "title": "Tarea ejemplo",
                            "column_id": 2
                        },
                        "message": "Task moved successfully"
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
        result = await move_task_service(task_id, new_column_id)
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