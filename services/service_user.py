from database.database import collection_users
from models.model_user import UserCreate
from datetime import datetime
from bson import ObjectId
import logging

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
        # Crear el documento del usuario con id y fechas automáticas
        user_dict = user.model_dump()
        user_dict["id"] = await get_next_id()
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
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise

async def get_user(user_id: int):
    try:
        logger.info(f"Fetching user with id: {user_id}")
        user = await collection_users.find_one({"id": user_id})
        if user:
            logger.info(f"User found: {user['username']}")
            return serialize_doc(user)
        logger.info(f"User with id {user_id} not found")
        return {"message": "User not found"}
    except Exception as e:
        logger.error(f"Error fetching user: {str(e)}")
        raise

async def update_user(user_id: int, user: UserCreate):
    try:
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
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        raise

async def delete_user(user_id: int):
    try:
        logger.info(f"Deleting user with id: {user_id}")
        deleted_user = await collection_users.delete_one({"id": user_id})
        if deleted_user.deleted_count:
            logger.info(f"User with id {user_id} deleted successfully")
            return {"message": "User deleted successfully"}
        logger.info(f"User with id {user_id} not found for deletion")
        return {"message": "User not found"}
    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}")
        raise








