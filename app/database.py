from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings

class Database:
    client: AsyncIOMotorClient = None
    
database = Database()

async def get_database():
    return database.client[settings.database_name]

async def connect_to_mongo():
    database.client = AsyncIOMotorClient(settings.mongodb_url)
    print(f"Connected to MongoDB at {settings.mongodb_url}")

async def close_mongo_connection():
    database.client.close()
    print("MongoDB connection closed")
