# Cofrinho Pessoal

Aplicação pessoal para controle de gastos e entradas de dinheiro.

## O que é

O Cofrinho Pessoal permite registrar **gastos** e **entradas** de dinheiro,
organizados por categorias e fontes de renda. Possui interface web com tema
escuro, API REST com autenticação JWT e documentação interativa via Swagger.

## Funcionalidades atuais

- Interface web com tema escuro (React + TypeScript)
- Login com autenticação JWT e renovação automática de token
- Dashboard com resumo financeiro (saldo, entradas, gastos por categoria)
- Cadastro de gastos, entradas, categorias e fontes de renda
- Histórico paginado com filtro por tipo (gastos/entradas)
- Filtros por data, valor e categoria/fonte via API
- Endpoint de resumo financeiro com saldo e gastos por categoria
- Isolamento multi-usuário (cada usuário vê apenas seus próprios dados)
- Testes automatizados: backend (116 testes) e frontend (120 testes)

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

## Links úteis

- [Frontend](http://localhost:5173) — interface web
- [Swagger UI](http://localhost:8000/api/docs/) — documentação interativa da API
- [Django Admin](http://localhost:8000/admin/) — painel de administração
