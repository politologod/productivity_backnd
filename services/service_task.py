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
    # Encontrar el último documento ordenado por id de forma descendente
    last_task = await collection_tasks.find_one(sort=[("id", -1)])
    if last_task:
        return last_task["id"] + 1
    return 1

async def get_tasks():
    tasks = await collection_tasks.find().to_list(length=100)
    return [serialize_doc(task) for task in tasks]

async def get_user_tasks(user_id: int):
    # Obtener tareas donde el usuario está asignado o es el creador
    tasks = await collection_tasks.find({
        "$or": [
            {"assigned_to": user_id},
            {"created_by": user_id}
        ]
    }).to_list(length=100)
    return [serialize_doc(task) for task in tasks]

async def create_task(task: TaskCreate, user_id: int):
    # Verificar que todos los usuarios asignados existan
    for assigned_id in task.assigned_to:
        user = await collection_users.find_one({"id": assigned_id})
        if not user:
            raise ValueError(f"User with id {assigned_id} not found")

    # Crear el documento de la tarea
    task_dict = task.model_dump()
    task_dict["id"] = await get_next_id()
    task_dict["created_by"] = user_id
    current_time = datetime.now()
    task_dict["created_at"] = current_time
    task_dict["updated_at"] = current_time
    
    new_task = await collection_tasks.insert_one(task_dict)
    if new_task.inserted_id:
        created_task = await collection_tasks.find_one({"_id": new_task.inserted_id})
        return {"task": serialize_doc(created_task), "message": "Task created successfully"}
    return {"message": "Failed to create task"}

async def get_task(task_id: int):
    task = await collection_tasks.find_one({"id": task_id})
    if task:
        return serialize_doc(task)
    return {"message": "Task not found"}

async def update_task(task_id: int, task: TaskCreate, user_id: int):
    # Verificar que el usuario tenga permiso para actualizar la tarea
    existing_task = await collection_tasks.find_one({"id": task_id})
    if not existing_task:
        return {"message": "Task not found"}
    
    if existing_task["created_by"] != user_id:
        return {"message": "You don't have permission to update this task"}

    # Verificar que todos los usuarios asignados existan
    for assigned_id in task.assigned_to:
        user = await collection_users.find_one({"id": assigned_id})
        if not user:
            raise ValueError(f"User with id {assigned_id} not found")

    task_dict = task.model_dump()
    task_dict["updated_at"] = datetime.now()
    
    updated_task = await collection_tasks.update_one(
        {"id": task_id},
        {"$set": task_dict}
    )
    
    if updated_task.modified_count:
        task = await collection_tasks.find_one({"id": task_id})
        return {"task": serialize_doc(task), "message": "Task updated successfully"}
    return {"message": "Failed to update task"}

async def delete_task(task_id: int, user_id: int):
    # Verificar que el usuario tenga permiso para eliminar la tarea
    task = await collection_tasks.find_one({"id": task_id})
    if not task:
        return {"message": "Task not found"}
    
    if task["created_by"] != user_id:
        return {"message": "You don't have permission to delete this task"}

    deleted_task = await collection_tasks.delete_one({"id": task_id})
    if deleted_task.deleted_count:
        return {"message": "Task deleted successfully"}
    return {"message": "Failed to delete task"}


