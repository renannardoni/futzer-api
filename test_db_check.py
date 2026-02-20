import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

async def check_db():
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.database_name]
    
    # Contar usuários
    users_count = await db.users.count_documents({})
    print(f"Total de usuários: {users_count}")
    
    # Contar quadras
    quadras_count = await db.quadras.count_documents({})
    print(f"Total de quadras: {quadras_count}")
    
    # Listar quadras
    if quadras_count > 0:
        print("\nQuadras no banco:")
        async for quadra in db.quadras.find():
            print(f"  - {quadra}")

asyncio.run(check_db())
