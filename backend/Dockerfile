FROM debian:bookworm-slim

# Instala uv (que gerencia o Python também)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app

# Copia arquivos de dependências e instala sem o grupo dev.
# O uv baixa automaticamente o Python definido no uv.lock.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copia o restante do código
COPY . .

EXPOSE 8000

# Aplica migrations e sobe o servidor
CMD [".venv/bin/python", "manage.py", "runserver", "0.0.0.0:8000"]
