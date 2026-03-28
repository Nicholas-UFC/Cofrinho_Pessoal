# Cofrinho Pessoal

Aplicação pessoal para controle de gastos e entradas de dinheiro.

## O que é

O Cofrinho Pessoal permite registrar **gastos** e **entradas** de dinheiro,
organizados por categorias e fontes de renda. Possui interface web com tema
escuro, API REST com autenticação JWT, documentação interativa via Swagger e
um **bot para WhatsApp** que permite registrar movimentações diretamente pelo
celular, sem abrir o navegador.

## Funcionalidades atuais

- Interface web com tema escuro (React + TypeScript)
- Login com autenticação JWT e renovação automática de token
- Dashboard com resumo financeiro (saldo, entradas, gastos por categoria)
- Gráficos interativos no dashboard (barras, linha temporal, categorias e fontes) via Recharts
- Layout responsivo com menu hambúrguer e drawer lateral no mobile
- Cadastro de gastos, entradas, categorias e fontes de renda
- Histórico paginado com filtro por tipo (gastos/entradas)
- Filtros por data, valor e categoria/fonte via API
- Endpoint de resumo financeiro com saldo e gastos por categoria
- Isolamento multi-usuário (cada usuário vê apenas seus próprios dados)
- Análise estática automática via pre-commit: complexidade ciclomática (xenon), tamanho de arquivos (500 linhas) e ESLint complexity
- **Bot para WhatsApp** — registre gastos, entradas e consulte o resumo do mês via mensagem, com fluxo guiado por menus, timeout de sessão e rate limit
- Testes automatizados: backend (251 testes, 97% cobertura) e frontend (113 testes)

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

## Links úteis

- [Frontend](http://localhost:5173) — interface web
- [Swagger UI](http://localhost:8000/api/docs/) — documentação interativa da API
- [Django Admin](http://localhost:8000/admin/) — painel de administração
- [WAHA Dashboard](http://localhost:3000) — gerenciamento da sessão WhatsApp
