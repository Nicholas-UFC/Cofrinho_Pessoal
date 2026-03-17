# Cofrinho Pessoal

Aplicação pessoal para controle de gastos e entradas de dinheiro.

## O que é

O Cofrinho Pessoal permite registrar **gastos** e **entradas** de dinheiro,
organizados por categorias e fontes de renda. A API expõe endpoints REST
com autenticação JWT e documentação interativa via Swagger.

## Funcionalidades atuais

- Cadastro de categorias de gastos e fontes de renda
- Registro de gastos e entradas com categoria, valor e data
- Filtros por data, valor e categoria/fonte
- Paginação automática (20 itens por página)
- Endpoint de resumo financeiro com saldo e gastos por categoria
- Autenticação JWT com renovação automática de token
- Isolamento multi-usuário (cada usuário vê apenas seus próprios dados)

## Stack

| Camada         | Tecnologia                       |
|----------------|----------------------------------|
| Backend        | Django 6 + Django REST Framework |
| Banco          | PostgreSQL 16 (Docker)           |
| Linguagem      | Python 3.14                      |
| Autenticação   | JWT via SimpleJWT                |
| Documentação   | drf-spectacular (Swagger UI)     |
| Containers     | Docker + Docker Compose          |

## Links úteis

- [Swagger UI](http://localhost:8000/api/docs/) — documentação interativa da API
- [Django Admin](http://localhost:8000/admin/) — painel de administração
