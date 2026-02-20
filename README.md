# Futzer API

Backend API para plataforma de aluguel de quadras esportivas.

## Stack
- **Python 3.11+**
- **FastAPI** - Framework web moderno e rápido
- **MongoDB** - Banco de dados NoSQL
- **Motor** - Driver async MongoDB
- **JWT** - Autenticação

## Estrutura do Projeto
```
futzer-api/
├── app/
│   ├── main.py           # Aplicação principal
│   ├── config.py         # Configurações
│   ├── database.py       # Conexão MongoDB
│   ├── models.py         # Modelos Pydantic
│   ├── auth.py           # Autenticação JWT
│   └── routes/
│       ├── auth.py       # Rotas de autenticação
│       └── quadras.py    # Rotas de quadras
├── requirements.txt
└── .env
```

## Setup

### 1. Criar ambiente virtual
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

### 2. Instalar dependências
```bash
pip install -r requirements.txt
```

### 3. Configurar MongoDB
- Instale MongoDB localmente ou use MongoDB Atlas (cloud)
- MongoDB local: https://www.mongodb.com/try/download/community
- MongoDB Atlas: https://www.mongodb.com/cloud/atlas/register

### 4. Configurar variáveis de ambiente
Copie `.env.example` para `.env` e configure:
```bash
cp .env.example .env
```

Edite `.env`:
```
MONGODB_URL=mongodb://localhost:27017  # ou sua URL do Atlas
DATABASE_NAME=futzer_db
SECRET_KEY=sua-chave-secreta-aqui
```

### 5. Rodar servidor
```bash
uvicorn app.main:app --reload
```

API disponível em: http://localhost:8000
Documentação automática: http://localhost:8000/docs

## Endpoints

### Autenticação
- `POST /api/auth/register` - Registrar usuário
- `POST /api/auth/login` - Login (retorna JWT token)
- `GET /api/auth/me` - Perfil do usuário autenticado

### Quadras
- `GET /api/quadras/` - Listar quadras
- `GET /api/quadras/{id}` - Detalhes da quadra
- `POST /api/quadras/` - Criar quadra (requer autenticação)
- `PUT /api/quadras/{id}` - Atualizar quadra (requer autenticação)
- `DELETE /api/quadras/{id}` - Deletar quadra (requer autenticação)

## Autenticação
A API usa JWT tokens. Para acessar rotas protegidas:

1. Registre um usuário ou faça login
2. Use o token retornado no header:
   ```
   Authorization: Bearer seu-token-aqui
   ```

## Deploy
- Railway: `railway up`
- Render: Connect GitHub repo
- Heroku: `git push heroku main`
