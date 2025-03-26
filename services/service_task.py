from database.database import collection_tasks, collection_users
from models.model_task import TaskCreate, Task
from datetime import datetime
from bson import ObjectId
import logging
from models.model_user import Role
from typing import List, Optional

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def serialize_doc(doc):
    """Convierte el documento de MongoDB a un diccionario serializable"""
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc

async def get_next_id():
    try:
        last_task = await collection_tasks.find_one(sort=[("id", -1)])
        if last_task:
            return last_task["id"] + 1
        return 1
    except Exception as e:
        logger.error(f"Error getting next task id: {str(e)}")
        raise

async def get_tasks(user_id: int, user_role: str) -> List[Task]:
    """Obtiene todas las tareas según el rol del usuario"""
    try:
        logger.info("Fetching tasks")
        # Si es admin, obtiene todas las tareas
        if user_role == "admin":
            cursor = collection_tasks.find()
        else:
            # Si no es admin, solo obtiene sus propias tareas
            cursor = collection_tasks.find({
                "$or": [
                    {"assigned_to": user_id},
                    {"created_by": user_id}
                ]
            })
        
        tasks = []
        async for doc in cursor:
            tasks.append(Task(**serialize_doc(doc)))
        
        logger.info(f"Found {len(tasks)} tasks")
        return tasks
    except Exception as e:
        logger.error(f"Error fetching tasks: {str(e)}")
        raise

async def get_user_tasks(user_id: int, current_user_id: int, current_user_role: str) -> List[Task]:
    """Obtiene las tareas de un usuario específico"""
    try:
        # Verificar si el usuario existe
        user = await collection_users.find_one({"id": user_id})
        if not user:
            raise ValueError(f"Usuario con id {user_id} no encontrado")

        # Solo permitir que los usuarios vean sus propias tareas o que los admins vean todas
        if current_user_role != "admin" and current_user_id != user_id:
            raise ValueError("No tienes permiso para ver las tareas de este usuario")

        logger.info(f"Fetching tasks for user {user_id}")
        cursor = collection_tasks.find({
            "$or": [
                {"assigned_to": user_id},
                {"created_by": user_id}
            ]
        })
        
        tasks = []
        async for doc in cursor:
            tasks.append(Task(**serialize_doc(doc)))
        
        logger.info(f"Found {len(tasks)} tasks for user {user_id}")
        return tasks
    except ValueError as e:
        logger.error(f"Validation error fetching user tasks: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error fetching user tasks: {str(e)}")
        raise

async def create_task(task: TaskCreate, current_user_id: int) -> Task:
    """Crea una nueva tarea"""
    try:
        # Verificar que el usuario creador existe
        creator = await collection_users.find_one({"id": current_user_id})
        if not creator:
            raise ValueError(f"Usuario creador con id {current_user_id} no encontrado")

        # Verificar que todos los usuarios asignados existan
        for assigned_id in task.assigned_to:
            user = await collection_users.find_one({"id": assigned_id})
            if not user:
                raise ValueError(f"Usuario asignado con id {assigned_id} no encontrado")

        # Crear el documento de la tarea
        task_dict = task.model_dump()
        task_dict["id"] = await get_next_id()
        task_dict["created_by"] = current_user_id
        task_dict["created_at"] = datetime.utcnow()
        task_dict["updated_at"] = datetime.utcnow()
        
        logger.info(f"Creating new task with id: {task_dict['id']}")
        result = await collection_tasks.insert_one(task_dict)
        
        if result.inserted_id:
            created_task = await collection_tasks.find_one({"_id": result.inserted_id})
            logger.info(f"Task created successfully with id: {created_task['id']}")
            return Task(**serialize_doc(created_task))
        raise ValueError("Error al crear la tarea")
    except ValueError as e:
        logger.error(f"Validation error creating task: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        raise

async def get_task(task_id: int):
    try:
        logger.info(f"Fetching task with id: {task_id}")
        task = await collection_tasks.find_one({"id": task_id})
        if task:
            logger.info(f"Task found with id: {task_id}")
            return serialize_doc(task)
        logger.info(f"Task with id {task_id} not found")
        return {"message": "Task not found"}
    except Exception as e:
        logger.error(f"Error fetching task: {str(e)}")
        raise

async def update_task(task_id: int, task: TaskCreate, current_user_id: int, current_user_role: str) -> Task:
    """Actualiza una tarea existente"""
    try:
        # Verificar si la tarea existe y los permisos
        existing_task = await collection_tasks.find_one({"_id": ObjectId(task_id)})
        if not existing_task:
            raise ValueError("Tarea no encontrada")
        
        if current_user_role != "admin" and existing_task["created_by"] != current_user_id:
            raise ValueError("No tienes permiso para actualizar esta tarea")

        task_dict = task.model_dump()
        task_dict["updated_at"] = datetime.utcnow()
        
        await collection_tasks.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": task_dict}
        )
        
        updated_task = await collection_tasks.find_one({"_id": ObjectId(task_id)})
        logger.info(f"Tarea {task_id} actualizada exitosamente")
        return Task(**serialize_doc(updated_task))
    except ValueError as e:
        logger.error(f"Error de validación: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error al actualizar tarea: {str(e)}")
        raise

async def delete_task(task_id: int, current_user_id: int, current_user_role: str) -> bool:
    """Elimina una tarea"""
    try:
        # Verificar si la tarea existe y los permisos
        existing_task = await collection_tasks.find_one({"_id": ObjectId(task_id)})
        if not existing_task:
            raise ValueError("Tarea no encontrada")
        
        if current_user_role != "admin" and existing_task["created_by"] != current_user_id:
            raise ValueError("No tienes permiso para eliminar esta tarea")

        result = await collection_tasks.delete_one({"_id": ObjectId(task_id)})
        logger.info(f"Tarea {task_id} eliminada exitosamente")
        return result.deleted_count > 0
    except ValueError as e:
        logger.error(f"Error de validación: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error al eliminar tarea: {str(e)}")
        raise

async def move_task(task_id: int, new_column_id: int, current_user_id: int, current_user_role: str) -> Task:
    """Mueve una tarea a una nueva columna"""
    try:
        # Verificar si la tarea existe y los permisos
        existing_task = await collection_tasks.find_one({"_id": ObjectId(task_id)})
        if not existing_task:
            raise ValueError("Tarea no encontrada")
        
        if current_user_role != "admin" and existing_task["created_by"] != current_user_id:
            raise ValueError("No tienes permiso para mover esta tarea")

        await collection_tasks.update_one(
            {"_id": ObjectId(task_id)},
            {
                "$set": {
                    "column_id": new_column_id,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        updated_task = await collection_tasks.find_one({"_id": ObjectId(task_id)})
        logger.info(f"Tarea {task_id} movida a la columna {new_column_id}")
        return Task(**serialize_doc(updated_task))
    except ValueError as e:
        logger.error(f"Error de validación: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error al mover tarea: {str(e)}")
        raise


