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
| Recharts          | Gráficos interativos (barras, linha)    |
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

Resumo financeiro com três cards e quatro gráficos interativos:

- **Saldo** — diferença entre entradas e gastos
- **Entradas** — total de receitas do usuário
- **Gastos** — total de despesas do usuário

Gráficos (Recharts):

| Gráfico                  | Tipo          | Descrição                              |
|--------------------------|---------------|----------------------------------------|
| Entradas vs Gastos       | Barras        | Comparação dos totais                  |
| Evolução mensal          | Linha         | Últimos 3 meses                        |
| Gastos por categoria     | Barras horiz. | Distribuição por categoria             |
| Entradas por fonte       | Barras horiz. | Distribuição por fonte de renda        |

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

## Layout responsivo

O layout adapta-se ao tamanho da tela:

- **Desktop** — menu lateral sempre visível
- **Mobile** — menu oculto por padrão; botão hambúrguer na `BarraTopo` abre um drawer lateral com animação (`translate-x`)

---

## Autenticação

O token JWT é armazenado no `localStorage` (`access` e `refresh`).

- Toda requisição recebe o header `Authorization: Bearer <token>` via interceptor do Axios.
- Em caso de resposta `401`, o Axios tenta renovar o token via `POST /api/token/refresh/`.
- Se a renovação falhar, os tokens são removidos e o usuário é redirecionado para `/login`.
- O `ContextoAutenticacao` lê o token ao carregar a página, valida a expiração e restaura a sessão.

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

- `ContextoAutenticacao` — estado inicial, login, logout, token expirado, is_staff
- `RotaPrivada` — redirecionamento sem autenticação, token inválido
- `BarraTopo` — exibição do usuário, dropdown, botão hambúrguer, link de admin
- `MenuLateral` — links de navegação, logout, drawer mobile (aberto/fechado)
- `FormularioGasto` — campos, submit, limpeza pós-submit, loading, mensagens
- `FormularioEntrada` — campos, submit, limpeza pós-submit, loading, mensagens
- `FormularioCategoriaFonte` — aba categoria vs fonte, submit, loading, mensagens
- `PaginaLogin` — renderização, redirecionamento, erros, estado "Entrando..."
- `PaginaPainel` — loading, cards, cores do saldo, gráficos, erro de API
- `PaginaCadastro` — abas, formulários, sucesso, erros, regressão paginação
- `PaginaHistorico` — lista, troca de aba, paginação, vazio, erro
- Testes de segurança — token expirado, token malformado, XSS, logout, 401
