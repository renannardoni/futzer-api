"""
Script de teste simplificado da API Futzer
Execute: python test_simple.py
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

def test():
    print("\n==================== TESTE DA API FUTZER ====================\n")
    
    # 1. Health Check
    print("1. Health Check...")
    r = requests.get("http://localhost:8000/health")
    print(f"   Status: {r.status_code} - {r.json()}")
    
    # 2. Registrar usuário (pode dar erro se já existir)
    print("\n2. Registrando usuario...")
    data = {"email": "teste2@futzer.com", "password": "senha123", "nome": "Maria Silva"}
    r = requests.post(f"{BASE_URL}/auth/register", json=data)
    print(f"   Status: {r.status_code}")
    if r.status_code in [200, 201]:
        print(f"   Usuario criado: {r.json()['email']}")
    elif r.status_code == 400:
        print("   Usuario ja existe! Continuando...")
    else:
        print(f"   Erro: {r.text}")
    
    # 3. Login
    print("\n3. Fazendo login...")
    data = {"username": "teste2@futzer.com", "password": "senha123"}
    r = requests.post(f"{BASE_URL}/auth/login", data=data)
    print(f"   Status: {r.status_code}")
    
    if r.status_code != 200:
        print("   ERRO no login! Abortando...")
        return
    
    token = r.json()["access_token"]
    print(f"   Token obtido: {token[:50]}...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 4. Obter dados do usuário
    print("\n4. Obtendo dados do usuario...")
    r = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        user = r.json()
        print(f"   Usuario: {user['nome']} ({user['email']})")
    
    # 5. Criar quadra
    print("\n5. Criando quadra de teste...")
    quadra = {
        "nome": "Quadra Teste via Script",
        "descricao": "Quadra criada automaticamente pelo script de teste",
        "endereco": {
            "rua": "Rua Teste, 123",
            "cidade": "São Paulo",
            "estado": "SP",
            "cep": "01234-567"
        },
        "coordenadas": {
            "lat": -23.5505,
            "lng": -46.6333
        },
        "precoPorHora": 120.0,
        "tipoPiso": "society",
        "imagemCapa": "https://example.com/quadra-teste.jpg",
        "avaliacao": 5.0
    }
    
    r = requests.post(f"{BASE_URL}/quadras/", json=quadra, headers=headers)
    print(f"   Status: {r.status_code}")
    
    if r.status_code in [200, 201]:
        quadra_criada = r.json()
        quadra_id = quadra_criada["id"]
        print(f"   Quadra criada com ID: {quadra_id}")
        print(f"   Nome: {quadra_criada['nome']}")
        print(f"   Preco: R$ {quadra_criada['preco_hora']:.2f}/hora")
    else:
        print(f"   Erro: {r.text}")
        quadra_id = None
    
    # 6. Listar quadras
    print("\n6. Listando todas as quadras...")
    r = requests.get(f"{BASE_URL}/quadras/")
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        quadras = r.json()
        print(f"   Total de quadras: {len(quadras)}")
        for q in quadras[:3]:  # Mostrar apenas as 3 primeiras
            print(f"     - {q['nome']} ({q['tipo']}) - R$ {q['preco_hora']}")
    
    # 7. Buscar por tipo
    print("\n7. Buscando quadras tipo 'society'...")
    r = requests.get(f"{BASE_URL}/quadras/?tipo=society")
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        print(f"   Encontradas: {len(r.json())} quadras")
    
    # 8. Atualizar quadra
    if quadra_id:
        print(f"\n8. Atualizando quadra {quadra_id}...")
        update = {"preco_hora": 150.00}
        r = requests.put(f"{BASE_URL}/quadras/{quadra_id}", json=update, headers=headers)
        print(f"   Status: {r.status_code}")
        if r.status_code == 200:
            print(f"   Novo preco: R$ {r.json()['preco_hora']:.2f}/hora")
    
    print("\n==================== TESTES CONCLUIDOS ====================\n")
    print("Dicas:")
    print("  - Acesse http://localhost:8000/docs para documentacao interativa")
    print("  - Modifique este script para seus testes")
    print("  - Use o token para testar endpoints protegidos")
    print("\n")

if __name__ == "__main__":
    try:
        test()
    except requests.exceptions.ConnectionError:
        print("\nERRO: Nao foi possivel conectar a API!")
        print("Certifique-se de que o servidor esta rodando.")
        print("Execute: python -m uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\nERRO: {e}")
