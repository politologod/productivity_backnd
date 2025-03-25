from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient("mongodb://hbdev62:c4YjKtK0gi3s8DNM@cluster0-shard-00-00.myx2l.mongodb.net:27017,cluster0-shard-00-01.myx2l.mongodb.net:27017,cluster0-shard-00-02.myx2l.mongodb.net:27017/?replicaSet=atlas-13dhjj-shard-0&ssl=true&authSource=admin&retryWrites=true&w=majority&appName=Cluster0")
database = client.FARM_DB

collection_tasks = database.tasks

users_collection = database.users

admin_collection = database.admin



async def get_database():
    return database





