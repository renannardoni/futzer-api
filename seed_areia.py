import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

async def seed():
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.database_name]
    quadra = {
        "nome": "Arena Beach SP",
        "descricao": "Arena de areia completa para beach tennis e futevôlei, com 4 quadras demarcadas, iluminação noturna e área de descanso com vestiários. Localizada no coração de Pinheiros.",
        "endereco": {
            "rua": "Rua dos Pinheiros, 800",
            "cidade": "São Paulo",
            "estado": "SP",
            "cep": "05422-001"
        },
        "coordenadas": {
            "lat": -23.5651,
            "lng": -46.6836
        },
        "tipoPiso": "areia",
        "modalidade": "aluguel",
        "precoPorHora": None,
        "avaliacao": 4.7,
        "telefone": "(11) 97777-3344",
        "imagemCapa": "https://images.unsplash.com/photo-1612872087720-bb876e2e67d1?w=800&h=600&fit=crop",
        "imagens": [
            "https://images.unsplash.com/photo-1612872087720-bb876e2e67d1?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&h=600&fit=crop",
        ],
        "owner_id": "admin",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    result = await db["quadras"].insert_one(quadra)
    print(f"Inserida: {result.inserted_id}")
    client.close()

asyncio.run(seed())
