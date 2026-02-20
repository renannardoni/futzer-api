from app.models import QuadraCreate
import json

data = {
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
    "precoPorHora": 100,
    "tipoPiso": "society",
    "imagemCapa": "http://test.com/img.jpg"
}

try:
    q = QuadraCreate(**data)
    print("Modelo criado com sucesso!")
    print("Dict by_alias:", q.dict(by_alias=True))
except Exception as e:
    print(f"Erro: {e}")
