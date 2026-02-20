import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
from datetime import datetime

async def fix_quadras():
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.database_name]
    
    # Buscar quadras sem created_at ou updated_at
    quadras_sem_data = await db.quadras.find({
        "$or": [
            {"created_at": {"$exists": False}},
            {"updated_at": {"$exists": False}}
        ]
    }).to_list(length=None)
    
    print(f"Encontradas {len(quadras_sem_data)} quadras sem datas")
    
    # Atualizar cada uma
    for quadra in quadras_sem_data:
        now = datetime.utcnow()
        result = await db.quadras.update_one(
            {"_id": quadra["_id"]},
            {"$set": {
                "created_at": now,
                "updated_at": now
            }}
        )
        print(f"Quadra {quadra['_id']} atualizada: {result.modified_count} modificações")
    
    print("Todas as quadras foram atualizadas!")
    client.close()

asyncio.run(fix_quadras())
