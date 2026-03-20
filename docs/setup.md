# Configuração local

## Pré-requisitos

- [Docker](https://www.docker.com/) e Docker Compose
- [uv](https://docs.astral.sh/uv/) (para rodar testes e ferramentas do backend localmente)
- [pnpm](https://pnpm.io/) (para rodar o frontend localmente)

## Subir com Docker

**1. Clone o repositório:**

```bash
git clone https://github.com/Nicholas-UFC/Cofrinho_Pessoal
cd Cofrinho_Pessoal
```

**2. Crie o arquivo de variáveis de ambiente:**

```bash
cp .env.example .env
```

Edite o `.env` com os valores desejados (banco, secret key, etc.).

**3. Suba os containers:**

```bash
docker compose up -d
```

Isso inicia o PostgreSQL (5432), o backend Django (8000) e o frontend React (5173).

**4. Crie o superusuário:**

```bash
docker exec cofrinho_backend .venv/bin/python manage.py createsuperuser
```

| Serviço  | URL                                  |
|----------|--------------------------------------|
| Frontend | <http://localhost:5173>              |
| API      | <http://localhost:8000>              |
| Admin    | <http://localhost:8000/admin>        |
| Swagger  | <http://localhost:8000/api/docs>     |

---

## Desenvolvimento local (sem Docker)

### Backend

**1. Suba apenas o banco:**

```bash
docker compose up -d db
```

**2. Instale as dependências e rode:**

```bash
cd backend
uv sync --all-groups
cp .env.example .env   # ajuste DATABASE_URL para localhost:5432
uv run python manage.py migrate
uv run python manage.py runserver
```

### Frontend

```bash
cd frontend
pnpm install
cp .env.example .env   # ajuste VITE_API_URL se necessário
pnpm dev
```

O frontend estará disponível em <http://localhost:5173>.

---

## Rodar os testes

```bash
# Backend
cd backend
uv run pytest -v

# Frontend
cd frontend
pnpm vitest run
```

## Configurar pre-commit

```bash
cd backend
uv run pre-commit install
```
