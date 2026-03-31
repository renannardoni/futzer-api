"""
Seed: Arena Prado — Quadra real de Campinas
Execução: cd futzer-api && python seed_arena_prado.py
"""
import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings


async def seed():
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.database_name]

    # Verifica se já existe
    existente = await db.quadras.find_one({"nome": "Arena Prado"})
    if existente:
        print("⚠️  Arena Prado já está cadastrada! Nada a fazer.")
        client.close()
        return

    quadra = {
        "nome": "Arena Prado",
        "descricao": (
            "Quadras de futebol society com grama sintética de qualidade e "
            "espaço para futevôlei. Iluminação noturna, vestiários e "
            "estacionamento. Localizada no bairro Vila João Jorge em Campinas."
        ),
        "endereco": {
            "rua": "R. Amilar Alves, 537 - Vila João Jorge",
            "cidade": "Campinas",
            "estado": "SP",
            "cep": "13073-116",
        },
        "coordenadas": {
            "lat": -22.9185,
            "lng": -47.0782,
        },
        "tipoPiso": "futebol",
        "modalidade": "aluguel",
        "precoPorHora": None,
        "avaliacao": 0.0,
        "telefone": "(19) 99840-7878",
        "imagemCapa": "",
        "imagens": [],
        "owner_id": "admin",
        "ativo": True,
        "horariosSemanais": {
            "seg": {"slots": [8, 9, 10, 11, 14, 15, 16, 17, 18, 19, 20, 21]},
            "ter": {"slots": [8, 9, 10, 11, 14, 15, 16, 17, 18, 19, 20, 21]},
            "qua": {"slots": [8, 9, 10, 11, 14, 15, 16, 17, 18, 19, 20, 21]},
            "qui": {"slots": [8, 9, 10, 11, 14, 15, 16, 17, 18, 19, 20, 21]},
            "sex": {"slots": [8, 9, 10, 11, 14, 15, 16, 17, 18, 19, 20, 21]},
            "sab": {"slots": [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]},
            "dom": {"slots": [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]},
        },
        "datasBloqueadas": [],
        "quadrasInternas": [],
        "reservas": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    result = await db.quadras.insert_one(quadra)
    print(f"✅ Arena Prado cadastrada com ID: {result.inserted_id}")
    client.close()


asyncio.run(seed())
