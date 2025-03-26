from database.database import collection_kanban_columns, collection_tasks
from models.model_kanban import KanbanColumnCreate
from datetime import datetime
import logging
from models.model_user import Role

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def serialize_doc(doc):
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc

async def get_next_column_id():
    try:
        last_column = await collection_kanban_columns.find_one(sort=[("id", -1)])
        if last_column:
            return last_column["id"] + 1
        return 1
    except Exception as e:
        logger.error(f"Error getting next column id: {str(e)}")
        raise

async def get_columns():
    try:
        logger.info("Fetching all kanban columns")
        columns = await collection_kanban_columns.find().sort("order", 1).to_list(length=100)
        
        # Obtener las tareas para cada columna
        for column in columns:
            tasks = await collection_tasks.find({"column_id": column["id"]}).to_list(length=100)
            column["tasks"] = [serialize_doc(task) for task in tasks]
            
        logger.info(f"Found {len(columns)} columns")
        return [serialize_doc(column) for column in columns]
    except Exception as e:
        logger.error(f"Error fetching columns: {str(e)}")
        raise

async def create_column(column: KanbanColumnCreate):
    try:
        # Crear el documento de la columna
        column_dict = column.model_dump()
        column_dict["id"] = await get_next_column_id()
        current_time = datetime.now()
        column_dict["created_at"] = current_time
        column_dict["updated_at"] = current_time
        column_dict["tasks"] = []
        
        logger.info(f"Creating new column with id: {column_dict['id']}")
        new_column = await collection_kanban_columns.insert_one(column_dict)
        
        if new_column.inserted_id:
            created_column = await collection_kanban_columns.find_one({"_id": new_column.inserted_id})
            logger.info(f"Column created successfully with id: {created_column['id']}")
            return {"column": serialize_doc(created_column), "message": "Column created successfully"}
        raise ValueError("Error al crear la columna")
    except ValueError as e:
        logger.error(f"Validation error creating column: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error creating column: {str(e)}")
        raise

async def update_column(column_id: int, column: KanbanColumnCreate):
    try:
        # Verificar que la columna existe
        existing_column = await collection_kanban_columns.find_one({"id": column_id})
        if not existing_column:
            raise ValueError(f"Columna con id {column_id} no encontrada")

        column_dict = column.model_dump()
        column_dict["updated_at"] = datetime.now()
        
        logger.info(f"Updating column with id: {column_id}")
        updated_column = await collection_kanban_columns.update_one(
            {"id": column_id},
            {"$set": column_dict}
        )
        
        if updated_column.modified_count:
            column = await collection_kanban_columns.find_one({"id": column_id})
            logger.info(f"Column updated successfully with id: {column_id}")
            return {"column": serialize_doc(column), "message": "Column updated successfully"}
        raise ValueError("Error al actualizar la columna")
    except ValueError as e:
        logger.error(f"Validation error updating column: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error updating column: {str(e)}")
        raise

async def delete_column(column_id: int):
    try:
        # Verificar que la columna existe
        column = await collection_kanban_columns.find_one({"id": column_id})
        if not column:
            raise ValueError(f"Columna con id {column_id} no encontrada")

        # Verificar si hay tareas en la columna
        tasks_count = await collection_tasks.count_documents({"column_id": column_id})
        if tasks_count > 0:
            raise ValueError("No se puede eliminar una columna que contiene tareas")

        logger.info(f"Deleting column with id: {column_id}")
        deleted_column = await collection_kanban_columns.delete_one({"id": column_id})
        if deleted_column.deleted_count:
            logger.info(f"Column deleted successfully with id: {column_id}")
            return {"message": "Column deleted successfully"}
        raise ValueError("Error al eliminar la columna")
    except ValueError as e:
        logger.error(f"Validation error deleting column: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error deleting column: {str(e)}")
        raise

async def move_task(task_id: int, new_column_id: int):
    try:
        # Verificar que la tarea existe
        task = await collection_tasks.find_one({"id": task_id})
        if not task:
            raise ValueError(f"Tarea con id {task_id} no encontrada")

        # Verificar que la nueva columna existe
        new_column = await collection_kanban_columns.find_one({"id": new_column_id})
        if not new_column:
            raise ValueError(f"Columna con id {new_column_id} no encontrada")

        # Actualizar la tarea con la nueva columna
        logger.info(f"Moving task {task_id} to column {new_column_id}")
        updated_task = await collection_tasks.update_one(
            {"id": task_id},
            {"$set": {"column_id": new_column_id}}
        )
        
        if updated_task.modified_count:
            task = await collection_tasks.find_one({"id": task_id})
            logger.info(f"Task moved successfully to column {new_column_id}")
            return {"task": serialize_doc(task), "message": "Task moved successfully"}
        raise ValueError("Error al mover la tarea")
    except ValueError as e:
        logger.error(f"Validation error moving task: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error moving task: {str(e)}")
        raise 