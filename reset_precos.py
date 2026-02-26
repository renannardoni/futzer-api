"""
Migração: define precoPorHora = null em todas as quadras existentes.
Execução: python reset_precos.py
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

async def reset():
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.database_name]

    result = await db.quadras.update_many(
        {},
        {"$unset": {"precoPorHora": "", "preco_por_hora": ""}}
    )
    print(f"✅ {result.modified_count} quadras atualizadas — preço removido.")
    client.close()

asyncio.run(reset())
