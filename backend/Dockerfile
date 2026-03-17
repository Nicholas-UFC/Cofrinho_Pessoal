FROM python:3.14-slim

# Instala uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app

# Força o uv a usar o Python da imagem em vez de baixar outro.
ENV UV_PYTHON_PREFERENCE=only-system

# Copia arquivos de dependências e instala sem o grupo dev
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copia o restante do código
COPY . .

EXPOSE 8000

CMD [".venv/bin/python", "manage.py", "runserver", "0.0.0.0:8000"]
