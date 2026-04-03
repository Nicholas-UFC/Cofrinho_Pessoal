---
name: Frontend
description: Documentação do frontend React + TypeScript
---

# Frontend

Interface web do Cofrinho Pessoal, construída com React 19 e TypeScript.

## Stack

| Ferramenta            | Finalidade                                |
|-----------------------|-------------------------------------------|
| React 19 + Vite       | Framework e bundler                       |
| TypeScript strict     | Tipagem estática                          |
| Tailwind CSS          | Estilização utilitária                    |
| React Router v6       | Roteamento client-side                    |
| fetch (nativo)        | Requisições HTTP com credentials: include |
| jwt-decode            | Leitura do payload do token               |
| Recharts              | Gráficos interativos (barras, linha)      |
| ESLint + Prettier     | Linting e formatação                      |
| Husky + lint-staged   | Pre-commit automático                     |
| Vitest                | Test runner                               |
| Testing Library       | Testes de componentes React               |
| MSW                   | Mock de API nos testes                    |
| jest-axe              | Testes de acessibilidade (axe-core)       |

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

Os tokens JWT ficam em **cookies httpOnly** — nunca expostos ao JavaScript.

- Todas as requisições usam `fetch` nativo com `credentials: "include"`, enviando os cookies automaticamente — sem header `Authorization`.
- Em caso de resposta `401`, o cliente tenta renovar o access token via `POST /api/token/refresh/` (também com `credentials: "include"`).
- Se a renovação falhar, a info do usuário é removida do `localStorage` e o usuário é redirecionado para `/login`.
- O `ContextoAutenticacao` gerencia o estado de autenticação (`isAuthenticated`, `username`, `isAdmin`) em memória.

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
pnpm test             # execução única
pnpm test:watch       # modo watch
pnpm test:coverage    # com relatório de cobertura
```

217 testes organizados em 25 arquivos. Cobertura por área:

| Área | O que é testado |
| --- | --- |
| `ContextoAutenticacao` | Estado inicial, login, logout, token expirado, is_staff |
| `RotaPrivada` | Redirecionamento sem autenticação, token inválido |
| `BarraTopo` | Exibição do usuário, dropdown, botão hambúrguer, link de admin |
| `MenuLateral` | Links de navegação, logout, drawer mobile (aberto/fechado) |
| `Layout` | Outlet, toggle de sidebar, overlay mobile |
| `FormularioGasto` | Campos, submit, loading, mensagens |
| `FormularioEntrada` | Campos, submit, loading, mensagens |
| `FormularioCategoriaFonte` | Aba categoria vs fonte, submit, loading |
| `PaginaLogin` | Renderização, redirecionamento, erros, loading |
| `PaginaPainel` | Cards, cores do saldo, gráficos, erro de API |
| `PaginaCadastro` | Abas, formulários, sucesso, erros |
| `PaginaHistorico` | Lista, troca de aba, paginação, vazio, erro |
| `GraficoBarrasHorizontais` | Título, estado vazio, renderização com dados |
| `GraficoEntradasVsGastos` | Título, valores zerados, saldo negativo |
| `GraficoLinhaTempo` | Título, dados vazios, 3 meses de dados |
| `useHistorico` | Loading, erro, dados, mudança de página |
| `api/autenticacao` | `login()` — corpo, tokens, erros 401/500 |
| `api/financas` | Todos os métodos CRUD + paginação automática |
| `api/axios` | Interceptor de token, refresh automático em 401 |
| `utils/graficos` | `labelMes`, `ultimos3Meses`, `buildLineData`, `buildCategoriaData`, `buildFonteData` |
| `utils/format` | Formatação BRL e datas |
| `App` | Roteamento — rotas públicas, protegidas sem/com autenticação |
| Segurança | Token expirado, token malformado, XSS, logout, interceptor 401 |
| Acessibilidade | PaginaLogin, BarraTopo, MenuLateral, FormularioCategoriaFonte (axe-core) |
