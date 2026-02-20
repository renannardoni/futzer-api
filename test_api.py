"""
Script de teste da API Futzer
Execute: python test_api.py
"""

import requests
import json
from typing import Optional

# Configurações
BASE_URL = "http://localhost:8000/api"
token: Optional[str] = None

def print_separator():
    print("\n" + "="*80 + "\n")

def print_response(response, title="Resposta"):
    print(f"🔹 {title}")
    print(f"Status: {response.status_code}")
    try:
        data = response.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except:
        print(response.text)
    print_separator()

# 1. REGISTRAR USUÁRIO
def registrar_usuario():
    print("📝 PASSO 1: Registrando novo usuário...")
    
    data = {
        "email": "teste@futzer.com",
        "password": "senha123",
        "nome": "João da Silva"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=data)
    print_response(response, "Usuário Registrado")
    
    if response.status_code == 400:
        print("⚠️  Usuário já existe! Vamos fazer login...")
    
    return response.status_code in [200, 201]

# 2. FAZER LOGIN
def fazer_login():
    global token
    print("🔐 PASSO 2: Fazendo login...")
    
    data = {
        "username": "teste@futzer.com",
        "password": "senha123"
    }
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    print_response(response, "Login Realizado")
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"✅ Token obtido: {token[:50]}...")
        print_separator()
        return True
    return False

# 3. OBTER INFORMAÇÕES DO USUÁRIO
def obter_usuario():
    print("👤 PASSO 3: Obtendo informações do usuário autenticado...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    
    print_response(response, "Dados do Usuário")
    return response.status_code == 200

# 4. CRIAR QUADRAS DE TESTE
def criar_quadras():
    print("⚽ PASSO 4: Criando quadras de teste...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    quadras = [
        {
            "nome": "Arena Paulista",
            "tipo": "society",
            "esporte": "Futebol",
            "descricao": "Quadra society com grama sintética de última geração",
            "preco_hora": 150.00,
            "localizacao": {
                "endereco": "Av. Paulista, 1000",
                "cidade": "São Paulo",
                "estado": "SP",
                "cep": "01310-100",
                "latitude": -23.5631,
                "longitude": -46.6554
            },
            "disponibilidade": {
                "dias_semana": ["segunda", "terca", "quarta", "quinta", "sexta", "sabado"],
                "horario_abertura": "08:00",
                "horario_fechamento": "22:00"
            },
            "comodidades": ["vestiario", "chuveiro", "estacionamento", "iluminacao", "lanchonete"],
            "imagens": ["https://example.com/arena-paulista.jpg"]
        },
        {
            "nome": "Quadra Beach Tennis Ipanema",
            "tipo": "areia",
            "esporte": "Beach Tennis",
            "descricao": "Quadra de areia perfeita para beach tennis",
            "preco_hora": 80.00,
            "localizacao": {
                "endereco": "Rua Visconde de Pirajá, 500",
                "cidade": "Rio de Janeiro",
                "estado": "RJ",
                "cep": "22410-002",
                "latitude": -22.9838,
                "longitude": -43.2095
            },
            "disponibilidade": {
                "dias_semana": ["segunda", "terca", "quarta", "quinta", "sexta", "sabado", "domingo"],
                "horario_abertura": "07:00",
                "horario_fechamento": "20:00"
            },
            "comodidades": ["chuveiro", "vestiario", "bar"],
            "imagens": ["https://example.com/beach-tennis.jpg"]
        },
        {
            "nome": "Ginásio Centro Olímpico",
            "tipo": "quadra",
            "esporte": "Basquete",
            "descricao": "Quadra coberta profissional de basquete",
            "preco_hora": 200.00,
            "localizacao": {
                "endereco": "Rua do Esporte, 250",
                "cidade": "Belo Horizonte",
                "estado": "MG",
                "cep": "30130-100",
                "latitude": -19.9167,
                "longitude": -43.9345
            },
            "disponibilidade": {
                "dias_semana": ["segunda", "terca", "quarta", "quinta", "sexta"],
                "horario_abertura": "06:00",
                "horario_fechamento": "23:00"
            },
            "comodidades": ["vestiario", "chuveiro", "estacionamento", "iluminacao", "arquibancada"],
            "imagens": ["https://example.com/basquete.jpg"]
        }
    ]
    
    quadras_criadas = []
    
    for i, quadra in enumerate(quadras, 1):
        print(f"\n📍 Criando quadra {i}/3: {quadra['nome']}")
        response = requests.post(f"{BASE_URL}/quadras/", json=quadra, headers=headers)
        
        if response.status_code in [200, 201]:
            quadra_data = response.json()
            quadras_criadas.append(quadra_data)
            print(f"✅ Quadra criada com ID: {quadra_data.get('id', 'N/A')}")
        else:
            print_response(response, f"Erro ao criar {quadra['nome']}")
    
    print_separator()
    return quadras_criadas

# 5. LISTAR TODAS AS QUADRAS
def listar_quadras():
    print("📋 PASSO 5: Listando todas as quadras...")
    
    response = requests.get(f"{BASE_URL}/quadras/")
    print_response(response, "Lista de Quadras")
    
    if response.status_code == 200:
        quadras = response.json()
        print(f"✅ Total de quadras encontradas: {len(quadras)}")
        print_separator()
        return quadras
    return []

# 6. BUSCAR COM FILTROS
def buscar_com_filtros():
    print("🔍 PASSO 6: Buscando quadras com filtros...")
    
    # Filtro 1: Por tipo
    print("\n🔸 Filtro 1: Quadras tipo 'society'")
    response = requests.get(f"{BASE_URL}/quadras/?tipo=society")
    print_response(response, "Quadras Society")
    
    # Filtro 2: Por cidade
    print("\n🔸 Filtro 2: Quadras em São Paulo")
    response = requests.get(f"{BASE_URL}/quadras/?cidade=São Paulo")
    print_response(response, "Quadras em SP")
    
    # Filtro 3: Por preço máximo
    print("\n🔸 Filtro 3: Quadras até R$ 100/hora")
    response = requests.get(f"{BASE_URL}/quadras/?preco_max=100")
    print_response(response, "Quadras até R$ 100")
    
    # Filtro 4: Múltiplos filtros
    print("\n🔸 Filtro 4: Society em SP até R$ 200")
    response = requests.get(f"{BASE_URL}/quadras/?tipo=society&cidade=São Paulo&preco_max=200")
    print_response(response, "Filtros Combinados")

# 7. ATUALIZAR UMA QUADRA
def atualizar_quadra(quadra_id: str):
    print(f"✏️  PASSO 7: Atualizando quadra {quadra_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    atualizacao = {
        "preco_hora": 175.00,
        "descricao": "Quadra recém reformada com melhorias!"
    }
    
    response = requests.put(
        f"{BASE_URL}/quadras/{quadra_id}",
        json=atualizacao,
        headers=headers
    )
    
    print_response(response, "Quadra Atualizada")

# 8. OBTER UMA QUADRA ESPECÍFICA
def obter_quadra(quadra_id: str):
    print(f"🔎 PASSO 8: Obtendo detalhes da quadra {quadra_id}...")
    
    response = requests.get(f"{BASE_URL}/quadras/{quadra_id}")
    print_response(response, "Detalhes da Quadra")

# 9. DELETAR UMA QUADRA
def deletar_quadra(quadra_id: str):
    print(f"🗑️  PASSO 9: Deletando quadra {quadra_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(f"{BASE_URL}/quadras/{quadra_id}", headers=headers)
    
    if response.status_code == 204:
        print("✅ Quadra deletada com sucesso!")
        print_separator()
    else:
        print_response(response, "Erro ao deletar")

# 10. TESTE DE HEALTH CHECK
def health_check():
    print("❤️  TESTE INICIAL: Health Check...")
    
    response = requests.get("http://localhost:8000/health")
    print_response(response, "Health Check")
    
    return response.status_code == 200

# FUNÇÃO PRINCIPAL
def main():
    print("\n" + "🚀 " * 20)
    print("     SCRIPT DE TESTE DA API FUTZER")
    print("🚀 " * 20)
    print_separator()
    
    try:
        # Teste inicial
        if not health_check():
            print("❌ API não está respondendo! Verifique se o servidor está rodando.")
            return
        
        # Fluxo de testes
        registrar_usuario()
        
        if not fazer_login():
            print("❌ Falha no login!")
            return
        
        obter_usuario()
        
        quadras_criadas = criar_quadras()
        
        todas_quadras = listar_quadras()
        
        buscar_com_filtros()
        
        if quadras_criadas:
            primeiro_id = quadras_criadas[0].get('id')
            
            if primeiro_id:
                atualizar_quadra(primeiro_id)
                obter_quadra(primeiro_id)
                
                # Pergunta antes de deletar
                print("\n⚠️  Deseja deletar a primeira quadra criada? (s/n)")
                # Descomente a linha abaixo se quiser confirmação
                # if input().lower() == 's':
                #     deletar_quadra(primeiro_id)
                
                print("💡 Dica: Descomente o código acima para deletar com confirmação")
                print_separator()
        
        print("\n✅ " * 20)
        print("     TODOS OS TESTES CONCLUÍDOS COM SUCESSO!")
        print("✅ " * 20)
        print("\n💡 Próximos passos:")
        print("   1. Acesse http://localhost:8000/docs para ver a documentação interativa")
        print("   2. Modifique este script para testar seus próprios cenários")
        print("   3. Conecte o frontend Next.js ao backend")
        print_separator()
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERRO: Não foi possível conectar à API!")
        print("   Certifique-se de que o servidor está rodando em http://localhost:8000")
        print("   Execute: python -m uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {e}")

if __name__ == "__main__":
    main()
