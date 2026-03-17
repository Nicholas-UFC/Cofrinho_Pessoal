# Configuração local

## Pré-requisitos

- [Docker](https://www.docker.com/) e Docker Compose
- [uv](https://docs.astral.sh/uv/) (apenas para rodar testes e ferramentas localmente)

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

Isso inicia o PostgreSQL na porta `5432` e o backend Django na porta `8000`.

**4. Crie o superusuário:**

```bash
docker exec cofrinho_backend .venv/bin/python manage.py createsuperuser
```

A API estará disponível em `http://localhost:8000`.

---

## Desenvolvimento local (sem Docker para o backend)

Se preferir rodar o Django diretamente na sua máquina (com o banco no Docker):

**1. Suba apenas o banco:**

```bash
docker compose up -d db
```

**2. Entre na pasta do backend e instale as dependências:**

```bash
cd backend
uv sync --all-groups
```

**3. Configure o `.env` do backend:**

```bash
cp .env.example .env
```

O `DATABASE_URL` deve apontar para `localhost:5432`.

**4. Aplique as migrations e inicie o servidor:**

```bash
uv run python manage.py migrate
uv run python manage.py runserver
```

---

## Rodar os testes

```bash
cd backend
uv run pytest
```

## Configurar pre-commit

```bash
cd backend
uv run pre-commit install
```
