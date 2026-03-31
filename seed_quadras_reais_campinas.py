"""
Seed: Quadras REAIS de Campinas — Futebol, Tênis, Beach Tennis, Futevôlei
Execução: cd futzer-api && python seed_quadras_reais_campinas.py

Verifica duplicatas antes de inserir (pelo nome).
"""
import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings


HORARIOS_PADRAO = {
    "seg": {"slots": [8, 9, 10, 11, 14, 15, 16, 17, 18, 19, 20, 21]},
    "ter": {"slots": [8, 9, 10, 11, 14, 15, 16, 17, 18, 19, 20, 21]},
    "qua": {"slots": [8, 9, 10, 11, 14, 15, 16, 17, 18, 19, 20, 21]},
    "qui": {"slots": [8, 9, 10, 11, 14, 15, 16, 17, 18, 19, 20, 21]},
    "sex": {"slots": [8, 9, 10, 11, 14, 15, 16, 17, 18, 19, 20, 21]},
    "sab": {"slots": [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]},
    "dom": {"slots": [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]},
}

QUADRAS = [
    # ===== FUTEBOL SOCIETY =====
    {
        "nome": "Arena Sports Campinas 2",
        "descricao": "Quadra de futebol society com grama sintética de alta qualidade. Estrutura moderna, bem avaliada (4.9 estrelas). Funciona a partir das 16h.",
        "endereco": {
            "rua": "Rua Leonor Ponessi Cappelli, 461",
            "cidade": "Campinas",
            "estado": "SP",
            "cep": "13060-788",
        },
        "coordenadas": {"lat": -22.9329, "lng": -47.0573},
        "tipoPiso": "futebol",
        "precoPorHora": None,
        "telefone": "(19) 99873-4633",
        "avaliacao": 4.9,
    },
    {
        "nome": "Society Campinas",
        "descricao": "Quadra de grama sintética com churrasqueira, bar com porções e estacionamento. Região do Shopping Parque das Bandeiras, bairro Ipaussurama.",
        "endereco": {
            "rua": "Av. Homero V. de Souza Camargo, 400 - Ipaussurama",
            "cidade": "Campinas",
            "estado": "SP",
            "cep": "13060-080",
        },
        "coordenadas": {"lat": -22.9401, "lng": -47.1092},
        "tipoPiso": "futebol",
        "precoPorHora": None,
        "telefone": "(19) 97402-5879",
        "avaliacao": 4.8,
    },
    {
        "nome": "Arena Prado",
        "descricao": "Quadras de futebol society com grama sintética e espaço para futevôlei. Boa iluminação noturna, vestiários e estacionamento. Vila João Jorge.",
        "endereco": {
            "rua": "R. Amilar Alves, 537 - Vila João Jorge",
            "cidade": "Campinas",
            "estado": "SP",
            "cep": "13073-116",
        },
        "coordenadas": {"lat": -22.9185, "lng": -47.0782},
        "tipoPiso": "futebol",
        "precoPorHora": None,
        "telefone": "(19) 99840-7878",
        "avaliacao": 0.0,
    },
    {
        "nome": "Umbro Soccer Center Campinas",
        "descricao": "Quadras de futebol society com grama sintética, placar eletrônico, vestiários, sport bar e quiosque com churrasqueiras. Dentro do clube União dos Viajantes.",
        "endereco": {
            "rua": "Rua Monte Líbano, 250 - Jd. Chapadão",
            "cidade": "Campinas",
            "estado": "SP",
            "cep": "13070-140",
        },
        "coordenadas": {"lat": -22.8825, "lng": -47.0647},
        "tipoPiso": "futebol",
        "precoPorHora": 135.0,
        "telefone": "(19) 3213-2598",
        "avaliacao": 0.0,
    },
    {
        "nome": "Golaço Academia de Futebol",
        "descricao": "Academia de futebol com mais de 20 anos de tradição. Locação de quadras society e escolinha de futebol. Próximo ao Parque Taquaral.",
        "endereco": {
            "rua": "R. Padre Domingos Giovanini, 156 - Parque Taquaral",
            "cidade": "Campinas",
            "estado": "SP",
            "cep": "13087-460",
        },
        "coordenadas": {"lat": -22.8722, "lng": -47.0541},
        "tipoPiso": "futebol",
        "precoPorHora": None,
        "telefone": "(19) 3243-6295",
        "avaliacao": 0.0,
    },

    # ===== TÊNIS =====
    {
        "nome": "Tella Tennis Campinas",
        "descricao": "Centro de tênis com 8 quadras rápidas e 3 de saibro. Aulas e locação para todos os níveis.",
        "endereco": {
            "rua": "Campinas",
            "cidade": "Campinas",
            "estado": "SP",
            "cep": "13000-000",
        },
        "coordenadas": {"lat": -22.9064, "lng": -47.0616},
        "tipoPiso": "tenis",
        "precoPorHora": None,
        "telefone": "(19) 3207-2836",
        "avaliacao": 0.0,
    },
    {
        "nome": "Tênis Clube de Campinas - Sede de Campo",
        "descricao": "Tradicional clube de tênis em Sousas com quadras de saibro e rápidas. Funcionamento: Ter-Sex 7h-21h20, Sáb/Dom 7h-19h.",
        "endereco": {
            "rua": "R. San Conrado, 115 - Sousas",
            "cidade": "Campinas",
            "estado": "SP",
            "cep": "13105-093",
        },
        "coordenadas": {"lat": -22.8641, "lng": -46.9711},
        "tipoPiso": "tenis",
        "precoPorHora": None,
        "telefone": "(19) 3258-1443",
        "avaliacao": 0.0,
    },

    # ===== AREIA (Beach Tennis / Futevôlei) =====
    {
        "nome": "Arena Vinci Esportes",
        "descricao": "Arena de areia profissional para beach tennis e futevôlei. Quadras de alta qualidade, bar, vestiários. Bairro Ipaussurama.",
        "endereco": {
            "rua": "Av. Dr. Homero V. de Souza Camargo, 1003 - Ipaussurama",
            "cidade": "Campinas",
            "estado": "SP",
            "cep": "13060-080",
        },
        "coordenadas": {"lat": -22.9395, "lng": -47.1105},
        "tipoPiso": "areia",
        "precoPorHora": None,
        "telefone": "",
        "avaliacao": 0.0,
    },
    {
        "nome": "Nova Beach Campinas",
        "descricao": "Arena completa de beach tennis com quadras profissionais, iluminação de alta performance, pet-friendly, vestiários e lounge social. Nova Campinas.",
        "endereco": {
            "rua": "Av. Dr. Jesuíno Marcondes Machado, 869 - Nova Campinas",
            "cidade": "Campinas",
            "estado": "SP",
            "cep": "13092-108",
        },
        "coordenadas": {"lat": -22.8939, "lng": -47.0542},
        "tipoPiso": "areia",
        "precoPorHora": None,
        "telefone": "(19) 99557-5156",
        "avaliacao": 0.0,
    },
    {
        "nome": "Arena Sergio Cavalcante",
        "descricao": "Arena de beach tennis em Barão Geraldo com estrutura profissional. Também possui unidade no Clube da Rhodia.",
        "endereco": {
            "rua": "Barão Geraldo",
            "cidade": "Campinas",
            "estado": "SP",
            "cep": "13083-000",
        },
        "coordenadas": {"lat": -22.8183, "lng": -47.0837},
        "tipoPiso": "areia",
        "precoPorHora": None,
        "telefone": "",
        "avaliacao": 0.0,
    },
    {
        "nome": "Sociedade Hípica de Campinas - Beach Tennis",
        "descricao": "Complexo com 6 quadras de areia dedicadas exclusivamente ao beach tennis. Estrutura de clube tradicional.",
        "endereco": {
            "rua": "R. Cel. Silva Telles, 570 - Cambuí",
            "cidade": "Campinas",
            "estado": "SP",
            "cep": "13024-000",
        },
        "coordenadas": {"lat": -22.8974, "lng": -47.0551},
        "tipoPiso": "areia",
        "precoPorHora": None,
        "telefone": "",
        "avaliacao": 0.0,
    },
    {
        "nome": "PUC-Campinas - Quadras de Areia",
        "descricao": "Duas quadras de areia (8x16m cada) para beach tennis, futevôlei, vôlei de areia e beach head. Abertas para locação.",
        "endereco": {
            "rua": "Rod. Dom Pedro I, km 136 - Parque das Universidades",
            "cidade": "Campinas",
            "estado": "SP",
            "cep": "13086-900",
        },
        "coordenadas": {"lat": -22.8345, "lng": -47.0520},
        "tipoPiso": "areia",
        "precoPorHora": None,
        "telefone": "",
        "avaliacao": 0.0,
    },
]


async def seed():
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.database_name]

    inseridas = 0
    puladas = 0

    for q in QUADRAS:
        existente = await db.quadras.find_one({"nome": q["nome"]})
        if existente:
            print(f"⏭️  {q['nome']} — já existe, pulando")
            puladas += 1
            continue

        doc = {
            **q,
            "modalidade": "aluguel",
            "imagemCapa": "",
            "imagens": [],
            "owner_id": "admin",
            "ativo": True,
            "horariosSemanais": HORARIOS_PADRAO,
            "datasBloqueadas": [],
            "quadrasInternas": [],
            "reservas": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        result = await db.quadras.insert_one(doc)
        print(f"✅ {q['nome']} — inserida (ID: {result.inserted_id})")
        inseridas += 1

    print(f"\n{'='*50}")
    print(f"Resultado: {inseridas} inseridas, {puladas} já existiam")
    client.close()


asyncio.run(seed())
