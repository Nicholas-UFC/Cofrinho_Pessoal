# Cofrinho Pessoal

Aplicação pessoal para controle de gastos e entradas de dinheiro.
Registre despesas e receitas, filtre por período e categoria, e acompanhe
seu saldo em tempo real via interface web e API REST.

---

## Stack

| Camada        | Tecnologia                           |
|---------------|--------------------------------------|
| Frontend      | React 19 + TypeScript + Vite         |
| Backend       | Django 6 + Django REST Framework     |
| Banco         | PostgreSQL 16 (Docker)               |
| Linguagem     | Python 3.14 / TypeScript strict      |
| Autenticação  | JWT via SimpleJWT                    |
| Documentação  | drf-spectacular (Swagger UI)         |
| Containers    | Docker + Docker Compose              |

---

## O que está implementado

- Interface web com tema escuro (React + TypeScript)
- Login com autenticação JWT e renovação automática de token
- Dashboard com resumo financeiro (saldo, entradas, gastos por categoria)
- Cadastro de gastos, entradas, categorias e fontes de renda
- Histórico paginado com filtro por tipo (gastos/entradas)
- Filtros por data, valor e categoria/fonte via API
- Endpoint de resumo com saldo e gastos por categoria
- Isolamento multi-usuário (cada usuário vê apenas seus próprios dados)
- Painel administrativo via Django Admin (acesso rápido pelo frontend para admins)
- Documentação interativa via Swagger UI
- Stack completa dockerizada (banco + backend + frontend)
- Testes automatizados: backend (pytest, 116 testes) e frontend (vitest, 120 testes)

## O que ainda não está implementado

- App mobile
- Integração com WhatsApp
- Integração com IA para categorização automática

## Objetivo futuro

Ser uma ferramenta completa de controle financeiro pessoal onde o usuário
possa registrar gastos de forma rápida via WhatsApp ou app mobile, com
categorização automática por IA e visualização clara do saldo e dos hábitos
de consumo.

---

## Início rápido

**Pré-requisitos:** Docker e Docker Compose instalados.

```bash
# 1. Clone o repositório
git clone https://github.com/Nicholas-UFC/Cofrinho_Pessoal
cd Cofrinho_Pessoal

# 2. Crie o arquivo de variáveis de ambiente
cp .env.example .env

# 3. Suba os containers (banco + backend + frontend)
docker compose up -d

# 4. Crie o superusuário
docker exec cofrinho_backend .venv/bin/python manage.py createsuperuser
```

| Serviço  | URL                                    |
|----------|----------------------------------------|
| Frontend | <http://localhost:5173>                |
| API      | <http://localhost:8000>                |
| Admin    | <http://localhost:8000/admin>          |
| Swagger  | <http://localhost:8000/api/docs>       |

---

## Rodar os testes

```bash
# Backend
cd backend && uv run pytest -v

# Frontend
cd frontend && pnpm vitest run
```

---

## Licença

[GNU AGPL v3.0](LICENSE)

---

## Documentação

Para entender a API, os modelos e como configurar o ambiente localmente,
rode a documentação completa com:

```bash
cd backend
uv run mkdocs serve
```

Acesse em `http://127.0.0.1:8001`.
