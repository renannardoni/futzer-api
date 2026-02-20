import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
from app.models import Quadra

async def test_serialization():
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.database_name]
    
    # Buscar uma quadra
    quadra_db = await db.quadras.find_one()
    if quadra_db:
        print("Quadra do DB:", quadra_db)
        print("\nTentando criar objeto Quadra...")
        
        try:
            quadra = Quadra(
                id=str(quadra_db["_id"]),
                nome=quadra_db["nome"],
                descricao=quadra_db["descricao"],
                endereco=quadra_db["endereco"],
                coordenadas=quadra_db["coordenadas"],
                precoPorHora=quadra_db.get("precoPorHora", quadra_db.get("preco_por_hora")),
                tipoPiso=quadra_db.get("tipoPiso", quadra_db.get("tipo_piso")),
                imagemCapa=quadra_db.get("imagemCapa", quadra_db.get("imagem_capa")),
                avaliacao=quadra_db.get("avaliacao", 0.0),
                owner_id=quadra_db.get("owner_id"),
                created_at=quadra_db["created_at"],
                updated_at=quadra_db["updated_at"]
            )
            print("Sucesso! Quadra criada:")
            print(quadra.dict())
            print("\nJSON:")
            print(quadra.json())
        except Exception as e:
            print(f"ERRO ao criar Quadra: {e}")
            import traceback
            traceback.print_exc()
    
    client.close()

asyncio.run(test_serialization())
