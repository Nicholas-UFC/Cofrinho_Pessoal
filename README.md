# Cofrinho Pessoal

Aplicação pessoal para controle de gastos e entradas de dinheiro.
Registre despesas e receitas, filtre por período e categoria, e acompanhe
seu saldo em tempo real via interface web, API REST ou diretamente pelo
WhatsApp.

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
| WhatsApp      | WAHA (WhatsApp HTTP API)             |

---

## O que está implementado

- Interface web com tema escuro (React + TypeScript)
- Login com autenticação JWT e renovação automática de token
- Dashboard com resumo financeiro (saldo, entradas, gastos por categoria)
- Gráficos interativos no dashboard (barras, linha temporal, categorias e fontes)
- Layout responsivo com menu hambúrguer e drawer lateral no mobile
- Cadastro de gastos, entradas, categorias e fontes de renda
- Histórico paginado com filtro por tipo (gastos/entradas)
- Filtros por data, valor e categoria/fonte via API
- Endpoint de resumo com saldo e gastos por categoria
- Isolamento multi-usuário (cada usuário vê apenas seus próprios dados)
- Painel administrativo via Django Admin (acesso rápido pelo frontend para admins)
- Documentação interativa via Swagger UI
- **Bot para WhatsApp** — registre gastos, entradas e consulte o resumo do mês via mensagem, com fluxo guiado por menus, timeout de sessão e rate limit
- Stack completa dockerizada (banco + backend + frontend + WAHA)
- Testes automatizados: backend (pytest, 251 testes, 97% cobertura) e frontend (vitest, 113 testes)

## O que ainda não está implementado

- App mobile
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

# 3. Suba os containers (banco + backend + frontend + WAHA)
docker compose up -d

# 4. Crie o superusuário
docker exec cofrinho_backend .venv/bin/python manage.py createsuperuser
```

| Serviço       | URL                                    |
|---------------|----------------------------------------|
| Frontend      | <http://localhost:5173>                |
| API           | <http://localhost:8000>                |
| Admin         | <http://localhost:8000/admin>          |
| Swagger       | <http://localhost:8000/api/docs>       |
| WAHA Dashboard| <http://localhost:3000>                |

### Variáveis de ambiente do WhatsApp

As variáveis abaixo são necessárias para ativar o bot:

| Variável                  | Descrição                                          |
|---------------------------|----------------------------------------------------|
| `WAHA_API_URL`            | URL do container WAHA (ex: `http://waha:3000`)     |
| `WAHA_API_KEY`            | Chave de autenticação da API WAHA                  |
| `WAHA_GROUP_ID`           | ID do grupo WhatsApp que o bot monitora            |
| `WAHA_SESSION`            | Nome da sessão WAHA (padrão: `default`)            |
| `WAHA_OWNER_USERNAME`     | Username Django do dono da conta (recebe os dados) |
| `WAHA_DASHBOARD_USERNAME` | Usuário do painel WAHA                             |
| `WAHA_DASHBOARD_PASSWORD` | Senha do painel WAHA                               |

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
