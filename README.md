# Cofrinho Pessoal

Aplicação pessoal para controle de gastos e entradas de dinheiro.
Registre despesas e receitas, filtre por período e categoria, e acompanhe
seu saldo em tempo real via API REST.

---

## Stack

| Camada        | Tecnologia                       |
|---------------|----------------------------------|
| Backend       | Django 6 + Django REST Framework |
| Banco (dev)   | SQLite                           |
| Banco (prod)  | PostgreSQL                       |
| Autenticação  | JWT via SimpleJWT                |
| Documentação  | drf-spectacular (Swagger UI)     |

---

## O que está implementado

- Cadastro de categorias de gastos e fontes de renda
- Registro de gastos e entradas com validação de valores
- Filtros por data, valor e categoria/fonte
- Paginação automática nas listagens (20 itens por página)
- Endpoint de resumo com saldo e gastos por categoria
- Autenticação JWT com renovação automática de token
- Painel administrativo via Django Admin
- Documentação interativa via Swagger UI

## O que ainda não está implementado

- Frontend web
- App mobile
- Integração com WhatsApp
- Integração com Google Gemini (IA para categorização automática)
- Deploy em produção (Docker, Nginx, PostgreSQL)

## Objetivo futuro

Ser uma ferramenta completa de controle financeiro pessoal onde o usuário
possa registrar gastos de forma rápida via WhatsApp ou app mobile, com
categorização automática por IA e visualização clara do saldo e dos hábitos
de consumo.

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

Acesse em `http://127.0.0.1:8000`.
