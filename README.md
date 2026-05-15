# Desafio Full Stack

Implementação do teste prático com API em FastAPI, autenticação JWT, CRUD de tarefas, migrations com Alembic, Docker Compose com PostgreSQL e cliente React Native.

## Estrutura

- `backend/`: API em FastAPI organizada em camadas (`domain`, `application`, `infrastructure`, `presentation`)
- `frontend/`: aplicativo React Native com login, listagem com pull-to-refresh e conclusão de tarefas
- `docker-compose.yml`: sobe PostgreSQL e API

## Requisitos

- Docker e Docker Compose
- Python 3.8+ para execução local do backend
- Node 18+ e npm para execução local do frontend

## Configuração

1. Copie `.env.example` para `.env`.
2. Ajuste os valores se necessário.

## Executar com Docker

```bash
cp .env.example .env
docker compose up --build
```

Esse comando faz o build local da API a partir de `backend/` e sobe a API junto com o banco de dados PostgreSQL.

A API ficará disponível em `http://localhost:8000`.

Para subir em background, use:

```bash
docker compose up --build -d
```

Para parar os containers, use:

```bash
docker compose down
```

## Executar backend localmente

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

### Endpoints principais

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/tasks`
- `POST /api/tasks`
- `PUT /api/tasks/{task_id}`
- `DELETE /api/tasks/{task_id}`

## Executar frontend localmente

```bash
cd frontend
cp .env.example .env
npm install
npm run start
```

Para rodar o frontend no navegador, use:

```bash
cd frontend
npm run web -- --port 8090
```

O frontend web ficará disponível em `http://localhost:8090`.

Se estiver usando emulador Android, ajuste `EXPO_PUBLIC_API_URL` para `http://10.0.2.2:8000/api`.

Credenciais demo para o app mobile:

- `owner@example.com`
- `secret123`

O app mobile foi mantido focado em leitura das tarefas e atualizacao do status. O CRUD completo permanece disponivel na API. O cadastro tambem esta disponivel para facilitar a obtencao de token no teste manual.

## Regras atendidas

- Cadastro e login com JWT
- Apenas o dono da tarefa pode alterar ou deletar a tarefa
- Usuário possui várias tarefas
- Migrations com Alembic
- Testes unitários para regras de negócio críticas
- Frontend React Native com login, listagem, pull-to-refresh e conclusão de tarefas

## Testes

```bash
cd backend
pytest
```