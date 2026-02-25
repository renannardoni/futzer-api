"""
Migração: converte valores antigos de tipo_piso → futebol/tenis no MongoDB.
Execução: python migrate_tipo_piso.py
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

LEGADO_FUTEBOL = {"society", "grama", "salao", "quadra", "campo", "areia"}

async def migrate():
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.database_name]

    # Busca todos os documentos que ainda têm valor antigo
    cursor = db.quadras.find({
        "$or": [
            {"tipoPiso": {"$in": list(LEGADO_FUTEBOL)}},
            {"tipo_piso": {"$in": list(LEGADO_FUTEBOL)}},
        ]
    })
    quadras = await cursor.to_list(length=None)
    print(f"Encontradas {len(quadras)} quadras com valores legados de tipo_piso.")

    updated = 0
    for q in quadras:
        raw = q.get("tipoPiso") or q.get("tipo_piso") or ""
        new_value = "futebol" if raw.lower() in LEGADO_FUTEBOL else raw

        result = await db.quadras.update_one(
            {"_id": q["_id"]},
            {"$set": {"tipoPiso": new_value, "tipo_piso": new_value}}
        )
        updated += result.modified_count
        print(f"  {q['_id']} | {raw!r} → {new_value!r}")

    print(f"\nMigração concluída: {updated} de {len(quadras)} documentos atualizados.")
    client.close()

asyncio.run(migrate())
