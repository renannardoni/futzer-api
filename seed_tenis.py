"""
Insere uma quadra de tênis de exemplo no MongoDB de produção.
Execução: python seed_tenis.py
"""
import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

async def seed():
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.database_name]

    quadra = {
        "nome": "Tennis Club SP",
        "descricao": "Quadra de tênis profissional em saibro com iluminação LED, vestiários completos e estacionamento. Ideal para treinos e jogos amadores.",
        "endereco": {
            "rua": "Rua Augusta, 2500",
            "cidade": "São Paulo",
            "estado": "SP",
            "cep": "01412-100",
        },
        "coordenadas": {
            "lat": -23.5558,
            "lng": -46.6619,
        },
        "precoPorHora": 120.0,
        "tipoPiso": "tenis",
        "imagemCapa": "https://images.unsplash.com/photo-1595435934249-5df7ed86e1c0?w=800&h=600&fit=crop",
        "imagens": [
            "https://images.unsplash.com/photo-1595435934249-5df7ed86e1c0?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1554068865-24cecd4e34b8?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1622279457486-62dcc4a431d6?w=1200&h=800&fit=crop",
        ],
        "avaliacao": 4.7,
        "telefone": "(11) 3456-7890",
        "owner_id": "admin",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    result = await db.quadras.insert_one(quadra)
    print(f"✅ Quadra inserida com ID: {result.inserted_id}")
    client.close()

asyncio.run(seed())
