import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

async def seed():
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.database_name]
    quadra = {
        "nome": "Beach Arena Campinas",
        "descricao": "Quadra de vôlei de praia com areia fina importada e iluminação LED",
        "endereco": {
            "rua": "Av. Norte Sul, 1200",
            "cidade": "Campinas",
            "estado": "SP",
            "cep": "13098-321"
        },
        "coordenadas": {
            "lat": -22.9056,
            "lng": -47.0608
        },
        "tipoPiso": "areia",
        "modalidade": "aluguel",
        "precoPorHora": 100.0,
        "avaliacao": 4.5,
        "telefone": "",
        "imagemCapa": "https://images.unsplash.com/photo-1612872087720-bb876e2e67d1?w=800&h=600&fit=crop",
        "imagens": [
            "https://images.unsplash.com/photo-1612872087720-bb876e2e67d1?w=800&h=600&fit=crop",
        ],
        "owner_id": "admin",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    result = await db["quadras"].insert_one(quadra)
    print(f"Inserida: {result.inserted_id}")
    client.close()

asyncio.run(seed())
