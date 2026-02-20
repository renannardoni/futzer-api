from app.models import Quadra
from datetime import datetime

# Simulando dados do MongoDB
created_quadra = {
    "_id": "507f1f77bcf86cd799439011",
    "nome": "Test",
    "descricao": "Desc",
    "endereco": {
        "rua": "R1",
        "cidade": "SP",
        "estado": "SP",
        "cep": "01234-567"
    },
    "coordenadas": {
        "lat": -23.5,
        "lng": -46.6
    },
    "preco_por_hora": 100.0,
    "tipo_piso": "society",
    "imagem_capa": "http://test.com/img.jpg",
    "avaliacao": 5.0,
    "owner_id": "12345",
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow()
}

try:
    quadra = Quadra(
        id=str(created_quadra["_id"]),
        nome=created_quadra["nome"],
        descricao=created_quadra["descricao"],
        endereco=created_quadra["endereco"],
        coordenadas=created_quadra["coordenadas"],
        precoPorHora=created_quadra["preco_por_hora"],
        tipoPiso=created_quadra["tipo_piso"],
        imagemCapa=created_quadra["imagem_capa"],
        avaliacao=created_quadra.get("avaliacao", 0.0),
        owner_id=created_quadra.get("owner_id"),
        created_at=created_quadra["created_at"],
        updated_at=created_quadra["updated_at"]
    )
    print("Quadra criada com sucesso!")
    print(quadra.dict())
except Exception as e:
    print(f"Erro ao criar Quadra: {e}")
    import traceback
    traceback.print_exc()
