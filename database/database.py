from motor.motor_asyncio import AsyncIOMotorClient
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Conexión a MongoDB
    client = AsyncIOMotorClient("mongodb://hbdev62:c4YjKtK0gi3s8DNM@cluster0-shard-00-00.myx2l.mongodb.net:27017,cluster0-shard-00-01.myx2l.mongodb.net:27017,cluster0-shard-00-02.myx2l.mongodb.net:27017/?replicaSet=atlas-13dhjj-shard-0&ssl=true&authSource=admin&retryWrites=true&w=majority&appName=Cluster0")
    logger.info("Connected to MongoDB successfully")
    
    # Obtener la base de datos
    database = client.FARM_DB
    logger.info("Database selected: FARM_DB")
    
    # Obtener las colecciones
    collection_tasks = database.tasks
    collection_users = database.users
    collection_admin = database.admin
    
    logger.info("Collections initialized successfully")
except Exception as e:
    logger.error(f"Error connecting to MongoDB: {str(e)}")
    raise

async def get_database():
    return database





