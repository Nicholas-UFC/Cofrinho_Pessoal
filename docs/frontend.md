---
name: Frontend
description: Documentação do frontend React + TypeScript
---

# Frontend

Interface web do Cofrinho Pessoal, construída com React 19 e TypeScript.

## Stack

| Ferramenta        | Finalidade                              |
|-------------------|-----------------------------------------|
| React 19 + Vite   | Framework e bundler                     |
| TypeScript strict | Tipagem estática                        |
| Tailwind CSS      | Estilização utilitária                  |
| React Router v6   | Roteamento client-side                  |
| Axios             | Requisições HTTP com interceptors JWT   |
| jwt-decode        | Leitura do payload do token             |
| ESLint + Prettier | Linting e formatação                    |
| Husky + lint-staged | Pre-commit automático                 |
| Vitest            | Test runner                             |
| Testing Library   | Testes de componentes React             |
| MSW               | Mock de API nos testes                  |

---

## Páginas

### Login (`/login`)

Tela inicial para usuários não autenticados. Redireciona para `/dashboard`
após login bem-sucedido.

### Dashboard (`/dashboard`)

Resumo financeiro com três cards:

- **Saldo** — diferença entre entradas e gastos
- **Entradas** — total de receitas do usuário
- **Gastos** — total de despesas do usuário

Consumido pelo endpoint `GET /api/financas/resumo/`.

### Cadastro (`/cadastro`)

Quatro abas para registro de dados:

| Aba        | Descrição                                |
|------------|------------------------------------------|
| Gasto      | Registra uma despesa com categoria       |
| Entrada    | Registra uma receita com fonte           |
| Categoria  | Cria uma categoria de gasto              |
| Fonte      | Cria uma fonte de renda                  |

### Histórico (`/historico`)

Lista paginada dos registros do usuário, com alternância entre gastos
e entradas. Exibe data, descrição, categoria/fonte e valor.

---

## Autenticação

O token JWT é armazenado no `localStorage` (`access` e `refresh`).

- Toda requisição recebe o header `Authorization: Bearer <token>` via interceptor do Axios.
- Em caso de resposta `401`, o Axios tenta renovar o token via `POST /api/token/refresh/`.
- Se a renovação falhar, os tokens são removidos e o usuário é redirecionado para `/login`.
- O `AuthContext` lê o token ao carregar a página, valida a expiração e restaura a sessão.

---

## Rodar localmente

```bash
cd frontend
pnpm install
cp .env.example .env
pnpm dev
```

Disponível em <http://localhost:5173>.

---

## Testes

```bash
cd frontend
pnpm vitest run       # execução única
pnpm vitest           # modo watch
```

Os testes cobrem:

- `AuthContext` — estado inicial, login, logout, token expirado
- `PrivateRoute` — redirecionamento sem autenticação
- `TopBar` — exibição do usuário, dropdown, link de admin
- `Sidebar` — links de navegação, logout
- `LoginPage` — renderização, redirecionamento, erros
- `DashboardPage` — loading, cards, cores, erro de API
- `CadastroPage` — abas, formulários, sucesso, erros
- `HistoricoPage` — lista, troca de aba, paginação, vazio, erro
- Testes de segurança — token expirado, token malformado, XSS, logout, 401
