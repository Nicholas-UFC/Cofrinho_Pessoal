# Configuração local

## Pré-requisitos

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (gerenciador de pacotes)

## Instalação

**1. Clone o repositório e entre na pasta do backend:**

```bash
git clone https://github.com/Nicholas-UFC/Cofrinho_Pessoal
cd Cofrinho_Pessoal/backend
```

**2. Instale as dependências:**

```bash
uv sync --all-groups
```

**3. Crie o arquivo de variáveis de ambiente:**

```bash
cp .env.example .env
```

Edite o `.env` com os valores do seu ambiente. Para desenvolvimento,
o banco SQLite é usado automaticamente quando `DEBUG=True`.

**4. Aplique as migrations:**

```bash
uv run python manage.py migrate
```

**5. Crie um superusuário:**

```bash
uv run python manage.py createsuperuser
```

**6. Inicie o servidor:**

```bash
uv run python manage.py runserver
```

A API estará disponível em `http://localhost:8000`.

## Rodar os testes

```bash
uv run pytest
```

## Configurar pre-commit

```bash
uv run pre-commit install
```
