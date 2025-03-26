from database.database import collection_users, collection_tasks
from models.model_user import UserCreate
from datetime import datetime
from bson import ObjectId
import logging
from services.service_auth import get_password_hash

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_next_id():
    try:
        last_user = await collection_users.find_one(sort=[("id", -1)])
        if last_user:
            return last_user["id"] + 1
        return 1
    except Exception as e:
        logger.error(f"Error getting next id: {str(e)}")
        raise

def serialize_doc(doc):
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc

async def get_users():
    try:
        logger.info("Fetching all users")
        users = await collection_users.find().to_list(length=100)
        logger.info(f"Found {len(users)} users")
        return [serialize_doc(user) for user in users]
    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}")
        raise

async def create_user(user: UserCreate):
    try:
        # Verificar si el email ya existe
        existing_user = await collection_users.find_one({"email": user.email})
        if existing_user:
            raise ValueError("El email ya está registrado")

        # Verificar si el username ya existe
        existing_username = await collection_users.find_one({"username": user.username})
        if existing_username:
            raise ValueError("El nombre de usuario ya está en uso")

        # Crear el documento del usuario con id y fechas automáticas
        user_dict = user.model_dump()
        user_dict["id"] = await get_next_id()
        
        # Hashear la contraseña antes de guardarla
        hashed_password = get_password_hash(user_dict["password"])
        user_dict["password"] = hashed_password
        
        current_time = datetime.now()
        user_dict["created_at"] = current_time
        user_dict["updated_at"] = current_time
        
        logger.info(f"Creating new user: {user.username}")
        new_user = await collection_users.insert_one(user_dict)
        
        if new_user.inserted_id:
            created_user = await collection_users.find_one({"_id": new_user.inserted_id})
            logger.info(f"User created successfully with id: {created_user['id']}")
            return {"user": serialize_doc(created_user), "message": "User created successfully"}
        return {"message": "Failed to create user"}
    except ValueError as e:
        logger.error(f"Validation error creating user: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise

async def get_user(user_id: int, include_tasks: bool = False):
    try:
        logger.info(f"Fetching user with id: {user_id}")
        user = await collection_users.find_one({"id": user_id})
        if not user:
            logger.info(f"User with id {user_id} not found")
            return None
            
        if include_tasks:
            # Obtener las tareas del usuario
            tasks = await collection_tasks.find({
                "$or": [
                    {"assigned_to": user_id},
                    {"created_by": user_id}
                ]
            }).to_list(length=100)
            user["tasks"] = [serialize_doc(task) for task in tasks]
            
        return serialize_doc(user)
    except Exception as e:
        logger.error(f"Error fetching user: {str(e)}")
        raise

async def update_user(user_id: int, user: UserCreate):
    try:
        # Verificar si el usuario existe
        existing_user = await collection_users.find_one({"id": user_id})
        if not existing_user:
            raise ValueError("Usuario no encontrado")

        # Verificar si el nuevo email ya existe (excluyendo el usuario actual)
        if user.email != existing_user["email"]:
            email_exists = await collection_users.find_one({"email": user.email})
            if email_exists:
                raise ValueError("El email ya está registrado")

        # Verificar si el nuevo username ya existe (excluyendo el usuario actual)
        if user.username != existing_user["username"]:
            username_exists = await collection_users.find_one({"username": user.username})
            if username_exists:
                raise ValueError("El nombre de usuario ya está en uso")

        user_dict = user.model_dump()
        user_dict["updated_at"] = datetime.now()
        
        logger.info(f"Updating user with id: {user_id}")
        updated_user = await collection_users.update_one(
            {"id": user_id},
            {"$set": user_dict}
        )
        
        if updated_user.modified_count:
            user = await collection_users.find_one({"id": user_id})
            logger.info(f"User updated successfully: {user['username']}")
            return {"user": serialize_doc(user), "message": "User updated successfully"}
        logger.info(f"User with id {user_id} not found for update")
        return {"message": "Failed to update user"}
    except ValueError as e:
        logger.error(f"Validation error updating user: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        raise

async def delete_user(user_id: int):
    try:
        # Verificar si el usuario existe
        existing_user = await collection_users.find_one({"id": user_id})
        if not existing_user:
            raise ValueError("Usuario no encontrado")

        logger.info(f"Deleting user with id: {user_id}")
        deleted_user = await collection_users.delete_one({"id": user_id})
        if deleted_user.deleted_count:
            logger.info(f"User with id {user_id} deleted successfully")
            return {"message": "User deleted successfully"}
        logger.info(f"User with id {user_id} not found for deletion")
        return {"message": "User not found"}
    except ValueError as e:
        logger.error(f"Validation error deleting user: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}")
        raise








