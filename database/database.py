from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "seekanban")

try:
    # Conexión a MongoDB
    client = AsyncIOMotorClient(MONGODB_URL)
    logger.info("Connected to MongoDB successfully")
    
    # Obtener la base de datos
    database = client[DATABASE_NAME]
    logger.info("Database selected: " + DATABASE_NAME)
    
    # Obtener las colecciones
    collection_tasks = database.tasks
    collection_users = database.users
    collection_statistics = database.statistics
    collection_kanban_columns = database.kanban_columns
    
    logger.info("Collections initialized successfully")
except Exception as e:
    logger.error(f"Error connecting to MongoDB: {str(e)}")
    raise

async def get_database():
    return database





