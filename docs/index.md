# Cofrinho Pessoal

Aplicação pessoal para controle de gastos e entradas de dinheiro.

## O que é

O Cofrinho Pessoal permite registrar **gastos** e **entradas** de dinheiro,
organizados por categorias e fontes de renda. A API expõe endpoints REST
com autenticação JWT e documentação interativa via Swagger.

## Funcionalidades atuais

- Cadastro de categorias de gastos
- Cadastro de fontes de renda
- Registro de gastos com categoria, valor e data
- Registro de entradas com fonte, valor e data
- Filtros por data, valor e categoria/fonte
- Paginação automática (20 itens por página)
- Endpoint de resumo financeiro com saldo e gastos por categoria
- Autenticação JWT com renovação automática de token

## Stack

| Camada         | Tecnologia                    |
|----------------|-------------------------------|
| Backend        | Django 6 + Django REST Framework |
| Banco (dev)    | SQLite                        |
| Banco (prod)   | PostgreSQL                    |
| Autenticação   | JWT via SimpleJWT             |
| Documentação   | drf-spectacular (Swagger UI)  |
| Servidor ASGI  | Uvicorn                       |

## Links úteis

- [Swagger UI](http://localhost:8000/api/docs/) — documentação interativa da API
- [Django Admin](http://localhost:8000/admin/) — painel de administração
