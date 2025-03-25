from database.database import collection_tasks, collection_users
from models.model_task import TaskCreate
from datetime import datetime
from bson import ObjectId
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def serialize_doc(doc):
    if doc:
        doc["_id"] = str(doc["_id"])
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

async def get_tasks():
    try:
        logger.info("Fetching all tasks")
        tasks = await collection_tasks.find().to_list(length=100)
        logger.info(f"Found {len(tasks)} tasks")
        return [serialize_doc(task) for task in tasks]
    except Exception as e:
        logger.error(f"Error fetching tasks: {str(e)}")
        raise

async def get_user_tasks(user_id: int):
    try:
        # Verificar si el usuario existe
        user = await collection_users.find_one({"id": user_id})
        if not user:
            raise ValueError(f"Usuario con id {user_id} no encontrado")

        logger.info(f"Fetching tasks for user {user_id}")
        tasks = await collection_tasks.find({
            "$or": [
                {"assigned_to": user_id},
                {"created_by": user_id}
            ]
        }).to_list(length=100)
        logger.info(f"Found {len(tasks)} tasks for user {user_id}")
        return [serialize_doc(task) for task in tasks]
    except ValueError as e:
        logger.error(f"Validation error fetching user tasks: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error fetching user tasks: {str(e)}")
        raise

async def create_task(task: TaskCreate, user_id: int):
    try:
        # Verificar que el usuario creador existe
        creator = await collection_users.find_one({"id": user_id})
        if not creator:
            raise ValueError(f"Usuario creador con id {user_id} no encontrado")

        # Verificar que todos los usuarios asignados existan
        for assigned_id in task.assigned_to:
            user = await collection_users.find_one({"id": assigned_id})
            if not user:
                raise ValueError(f"Usuario asignado con id {assigned_id} no encontrado")

        # Crear el documento de la tarea
        task_dict = task.model_dump()
        task_dict["id"] = await get_next_id()
        task_dict["created_by"] = user_id
        current_time = datetime.now()
        task_dict["created_at"] = current_time
        task_dict["updated_at"] = current_time
        
        logger.info(f"Creating new task with id: {task_dict['id']}")
        new_task = await collection_tasks.insert_one(task_dict)
        
        if new_task.inserted_id:
            created_task = await collection_tasks.find_one({"_id": new_task.inserted_id})
            logger.info(f"Task created successfully with id: {created_task['id']}")
            return {"task": serialize_doc(created_task), "message": "Task created successfully"}
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

async def update_task(task_id: int, task: TaskCreate, user_id: int):
    try:
        # Verificar que la tarea existe
        existing_task = await collection_tasks.find_one({"id": task_id})
        if not existing_task:
            raise ValueError(f"Tarea con id {task_id} no encontrada")
        
        # Verificar que el usuario tenga permiso para actualizar la tarea
        if existing_task["created_by"] != user_id:
            raise ValueError("No tienes permiso para actualizar esta tarea")

        # Verificar que todos los usuarios asignados existan
        for assigned_id in task.assigned_to:
            user = await collection_users.find_one({"id": assigned_id})
            if not user:
                raise ValueError(f"Usuario asignado con id {assigned_id} no encontrado")

        task_dict = task.model_dump()
        task_dict["updated_at"] = datetime.now()
        
        logger.info(f"Updating task with id: {task_id}")
        updated_task = await collection_tasks.update_one(
            {"id": task_id},
            {"$set": task_dict}
        )
        
        if updated_task.modified_count:
            task = await collection_tasks.find_one({"id": task_id})
            logger.info(f"Task updated successfully with id: {task_id}")
            return {"task": serialize_doc(task), "message": "Task updated successfully"}
        raise ValueError("Error al actualizar la tarea")
    except ValueError as e:
        logger.error(f"Validation error updating task: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error updating task: {str(e)}")
        raise

async def delete_task(task_id: int, user_id: int):
    try:
        # Verificar que la tarea existe
        task = await collection_tasks.find_one({"id": task_id})
        if not task:
            raise ValueError(f"Tarea con id {task_id} no encontrada")
        
        # Verificar que el usuario tenga permiso para eliminar la tarea
        if task["created_by"] != user_id:
            raise ValueError("No tienes permiso para eliminar esta tarea")

        logger.info(f"Deleting task with id: {task_id}")
        deleted_task = await collection_tasks.delete_one({"id": task_id})
        if deleted_task.deleted_count:
            logger.info(f"Task deleted successfully with id: {task_id}")
            return {"message": "Task deleted successfully"}
        raise ValueError("Error al eliminar la tarea")
    except ValueError as e:
        logger.error(f"Validation error deleting task: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error deleting task: {str(e)}")
        raise


