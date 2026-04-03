# Changelog

Todos os registros de mudanças deste projeto estão documentados aqui.
O formato segue [Versionamento Semântico](https://semver.org/): `MAJOR.MINOR.PATCH`.

- **MAJOR** — mudança que quebra compatibilidade (banco, API, infra)
- **MINOR** — nova funcionalidade sem quebrar nada existente
- **PATCH** — correção de bug

---

## [1.10.0] — 2026-04-03 — `feat/melhorias-arquitetura`

### 🔒 security: adiciona autenticação por token no webhook do WhatsApp
> Endpoint `/api/whatsapp/webhook/` aceitava qualquer POST sem validação. Agora exige o header `X-Webhook-Secret` com o valor de `WAHA_WEBHOOK_SECRET`. Quando a variável está vazia, aceita tudo (modo dev). Retorna 403 silencioso para tokens inválidos.
- Adicionados: _(nenhum)_
- Modificados: `backend/config/settings.py`, `backend/whatsapp/views.py`, `backend/whatsapp/tests/test_webhook_autenticacao.py`, `.env.example`

### ⚡ perf: adiciona índices compostos em Gasto e Entrada
> Queries de listagem com filtros `data__gte`, `data__lte` e `categoria`/`fonte` faziam full scan. Quatro índices compostos cobrem os padrões de acesso mais frequentes dos ViewSets.
- Adicionados: `backend/financas/migrations/0006_entrada_idx_entrada_usuario_data_and_more.py`
- Modificados: `backend/financas/models.py`

### 🏗️ arch: extrai service layer para criar e editar gastos e entradas
> Lógica de `Gasto.objects.create()` e `Entrada.objects.create()` estava duplicada nos handlers do bot e nos serializers da API REST. Centraliza em `financas/services/` para garantir uma única fonte de verdade para regras de negócio futuras.
- Adicionados: `backend/financas/services/__init__.py`, `backend/financas/services/gasto.py`, `backend/financas/services/entrada.py`
- Modificados: `backend/financas/serializers.py`, `backend/whatsapp/services/handlers_gasto.py`, `backend/whatsapp/services/handlers_entrada.py`, `backend/whatsapp/services/handlers_edicao.py`

---

## [1.9.0] — 2026-04-03 — `fix/waha-noweb-webhook`

### 🔥 refactor: remove services.py legado substituído pelo pacote services/
- Removidos: `backend/whatsapp/services.py`

### 🐛 fix: remove validação de API key e filtro fromMe do webhook
> WAHA NOWEB não envia o header X-Api-Key e não dispara eventos para mensagens com fromMe=True enviadas pelo celular.
- Modificados: `backend/whatsapp/views.py`

### 🐳 docker: ativa NOWEB store e configura headers de webhook
- Modificados: `docker-compose.yml`

### 📝 docs: atualiza README e MkDocs com CRUD de gastos e entradas via WhatsApp
- Modificados: `README.md`, `docs/whatsapp/bot.md`

### 📝 docs: adiciona regra de atualização do CHANGELOG antes de todo merge
- Modificados: `CLAUDE.md`

### 🧹 style: formata código com ruff
> Reformatação automática em 42 arquivos Python. Nenhuma lógica alterada.
- Modificados: `backend/config/settings.py`, `backend/financas/models.py`, `backend/financas/validators.py`, `backend/financas/views.py`, `backend/whatsapp/models.py`, `backend/whatsapp/services/__init__.py`, `backend/whatsapp/services/cliente_waha.py`, `backend/whatsapp/services/handlers_crud.py`, `backend/whatsapp/services/handlers_gasto.py`, `backend/whatsapp/services/utils.py` e 32 arquivos de testes

### 🐛 fix: corrige 23 erros de linting reportados pelo ruff
> Erros em arquivos não re-verificados desde que as regras foram ativadas (pre-commit só checa staged files).
- `ANN`: type hints em `backend/config/urls.py` e `backend/financas/autenticacao.py`
- `PLC0415`: imports movidos para o topo em `backend/financas/tests/test_queries.py`, `test_view_idempotencia.py`, `test_view_ordenacao.py`, `test_auditoria_integracao.py`
- `SIM105`: `try/except/pass` → `contextlib.suppress` em `backend/whatsapp/services/handlers_exclusao.py`
- `PLR0911`: helpers extraídos em `handlers_edicao.py`, `handlers_listagem.py` e `processador.py`
- Modificados: `backend/config/urls.py`, `backend/financas/autenticacao.py`, `backend/financas/tests/test_auditoria_integracao.py`, `test_queries.py`, `test_view_idempotencia.py`, `test_view_ordenacao.py`, `backend/whatsapp/services/handlers_edicao.py`, `handlers_exclusao.py`, `handlers_listagem.py`, `processador.py`

### ✅ test: atualiza testes para comportamento atual do webhook
> Dois testes verificavam comportamentos removidos no commit de NOWEB e não foram atualizados na época.
- `test_webhook_ignora_from_me_false` → `test_webhook_processa_from_me_false`: `fromMe=False` agora é processado
- `test_webhook_autenticacao.py`: 2 testes que esperavam `403` atualizados para `200`
- Modificados: `backend/whatsapp/tests/test_webhook.py`, `backend/whatsapp/tests/test_webhook_autenticacao.py`

### 📝 docs: atualiza contagens de testes e descrição do bot
- Modificados: `README.md`, `docs/frontend.md`, `docs/index.md`

### 📝 docs: corrige documentação de autenticação (cookies httpOnly, fetch, URL logout)
- `docs/frontend.md`: stack corrigida (Axios → fetch nativo); seção Autenticação corrigida (localStorage+Bearer → cookies httpOnly+credentials:include)
- `docs/api/autenticacao.md`: URL do logout corrigida (`/api/logout/` → `/api/token/logout/`)
- `.gitignore`: entrada para `cofrinho_contexto.txt`
- Modificados: `.gitignore`, `docs/api/autenticacao.md`, `docs/frontend.md`

---

## [1.8.0] — 2026-04-02

### 🗃️ feat: adiciona atualizado_em em Gasto e Entrada
- Novos: `backend/financas/migrations/0005_entrada_atualizado_em_gasto_atualizado_em.py`
- Modificados: `backend/financas/models.py`

### ♻️ refactor: divide services.py em módulos
- Novos: `backend/whatsapp/services/__init__.py`, `cliente_waha.py`, `handlers_entrada.py`, `handlers_gasto.py`, `processador.py`, `utils.py`
- Modificados: `backend/whatsapp/tests/test_rate_limit.py`, `test_timeout.py`

### 🗃️ feat: adiciona estados de CRUD ao SessaoConversa
- Novos: `backend/whatsapp/migrations/0002_alter_sessaoconversa_estado.py`
- Modificados: `backend/whatsapp/models.py`

### ✨ feat: adiciona opções 4 e 5 ao menu do WhatsApp
- Modificados: `backend/whatsapp/services/processador.py`, `utils.py`, `tests/test_models_whatsapp.py`

### ✨ feat: listagem paginada de gastos e entradas via WhatsApp
- Novos: `backend/whatsapp/services/handlers_crud.py`, `handlers_listagem.py`, `tests/test_fluxo_listar_entradas.py`, `tests/test_fluxo_listar_gastos.py`

### ✨ feat: exclusão de gastos e entradas via WhatsApp
- Novos: `backend/whatsapp/services/handlers_exclusao.py`, `tests/test_fluxo_excluir_entrada.py`, `tests/test_fluxo_excluir_gasto.py`

### ✨ feat: edição de gastos e entradas via WhatsApp
- Novos: `backend/whatsapp/services/handlers_edicao.py`, `tests/test_fluxo_editar_entrada.py`, `tests/test_fluxo_editar_gasto.py`

### ✅ test: testes para opções 4/5 do menu e funções de formatação
- Modificados: `backend/whatsapp/tests/test_fluxo_conversa.py`, `test_services_utils.py`

---

## [1.7.0] — 2026-04-01

### 📝 docs: atualiza autenticação para cookies httpOnly e contagem de testes
- Modificados: `README.md`, `docs/api/autenticacao.md`

### 🐳 docker: copia scripts/ antes do pnpm install no Dockerfile do frontend
- Modificados: `frontend/Dockerfile`

### 🔨 script: backup semanal do banco para Google Drive via pg_dump
- Novos: `scripts/backup_db.ps1`, `scripts/backup_db.Tests.ps1`
- Modificados: `.env.example`

### ✅ tests: torna padrões de erro nos testes de integração mais específicos
- Modificados: `scripts/backup_db.Tests.ps1`

### ♻️ refactor: substitui Axios por fetch nativo no frontend
- Novos: `frontend/src/api/cliente.ts`, `src/api/__tests__/cliente.test.ts`
- Modificados: `frontend/package.json`, `pnpm-lock.yaml`, `src/api/autenticacao.ts`, `src/api/financas.ts`, `scripts/verificar-pacotes-seguros.js`
- Removidos: `frontend/src/api/axios.ts`

---

## [1.6.0] — 2026-03-31

### 🔒 security: configura headers, cookies e rate limiting seguros (OWASP)
- Modificados: `backend/config/settings.py`, `backend/financas/middleware.py`

### 🔒 security: adiciona política de senhas e validação de caracteres perigosos (OWASP)
- Modificados: `backend/financas/serializers.py`, `backend/financas/validators.py`, `tests/test_serializers.py`

### 🔒 security: implementa logout com blacklist de tokens JWT e error handlers genéricos (OWASP)
- Modificados: `backend/config/urls.py`

### 🔒 security: adiciona hash de integridade SHA-256 ao modelo LogAuditoria (OWASP)
- Novos: `backend/financas/migrations/0004_hash_integridade_log_auditoria.py`
- Modificados: `backend/financas/models.py`

### 🔒 security: valida X-Api-Key no webhook e adiciona logging de falhas HTTP (OWASP)
- Modificados: `backend/whatsapp/services.py`, `backend/whatsapp/views.py`

### ✅ tests: adiciona testes de regressão para todos os controles de segurança OWASP
- Novos: `backend/conftest.py`, `financas/tests/test_error_handlers.py`, `test_log_integridade.py`, `test_log_sanitizacao.py`, `test_logout.py`, `test_password_policy.py`, `test_security_headers.py`, `test_throttling.py`, `test_validacao_caracteres.py`, `whatsapp/tests/conftest.py`, `whatsapp/tests/test_webhook_autenticacao.py`

### 🔒 security: bloqueia versões comprometidas do axios via pnpm overrides e postinstall
- Novos: `frontend/scripts/verificar-pacotes-seguros.js`
- Modificados: `frontend/package.json`, `pnpm-lock.yaml`

### 🔒 security: corrige vulnerabilidades em dependências de desenvolvimento
- Modificados: `frontend/package.json`, `pnpm-lock.yaml`, `scripts/verificar-pacotes-seguros.js`

### 🔒 security: autenticação via cookies httpOnly no backend (OWASP prática 76)
- Novos: `backend/financas/autenticacao.py`, `tests/test_auth_cookies.py`
- Modificados: `backend/config/settings.py`, `config/urls.py`, `financas/tests/test_auditoria_integracao.py`, `test_logout.py`, `test_queries.py`, `test_view_*.py` (múltiplos)

### 🔒 security: migra tokens JWT do localStorage para cookies httpOnly (OWASP 76)
- Modificados: `frontend/src/api/autenticacao.ts`, `src/api/axios.ts`, `src/components/BarraTopo.tsx`, `src/components/MenuLateral.tsx`, `src/context/ContextoAutenticacao.tsx`, `src/context/useAutenticacao.ts`, `src/test/security.test.tsx`, e testes relacionados

### 🔒 security: autoComplete, validação zod nos formulários e corrige override brace-expansion (OWASP)
- Modificados: `frontend/package.json`, `pnpm-lock.yaml`, `src/components/formularios/FormularioEntrada.tsx`, `FormularioGasto.tsx`, `src/pages/PaginaLogin.tsx`

---

## [1.5.0] — 2026-03-30

### 🧪 test: adiciona test_serializers para validação isolada dos serializers
- Novos: `backend/financas/tests/test_serializers.py`

### 🧪 test: adiciona test_queries para proteção contra N+1 em todos os endpoints
- Novos: `backend/financas/tests/test_queries.py`
- Modificados: `backend/financas/views.py`

### 🧪 test: adiciona test_models_whatsapp para SessaoConversa
- Novos: `backend/whatsapp/tests/test_models_whatsapp.py`

### 🧪 test: adiciona test_services_utils para funções utilitárias do whatsapp
- Novos: `backend/whatsapp/tests/test_services_utils.py`

### 🧪 test: adiciona test_queries_whatsapp para proteção contra N+1
- Novos: `backend/whatsapp/tests/test_queries_whatsapp.py`

### 🧪 test: adiciona test_view_jwt para edge cases de autenticação JWT
- Novos: `backend/financas/tests/test_view_jwt.py`

### 🧪 test: adiciona test_view_ordenacao para ordering padrão dos endpoints
- Novos: `backend/financas/tests/test_view_ordenacao.py`

### 🧪 test: adiciona test_view_idempotencia para DELETE, PUT e PATCH
- Novos: `backend/financas/tests/test_view_idempotencia.py`

### 🙈 chore: adiciona node_modules ao .gitignore
- Modificados: `.gitignore`

### ✅ test: adiciona cobertura completa de testes para o frontend
- Novos: `frontend/src/App.test.tsx`, `src/api/__tests__/autenticacao.test.ts`, `src/api/__tests__/axios.test.ts`, `src/api/__tests__/financas.test.ts`, `src/components/__tests__/Layout.test.tsx`, `src/components/graficos/__tests__/GraficoBarrasHorizontais.test.tsx`, `GraficoEntradasVsGastos.test.tsx`, `GraficoLinhaTempo.test.tsx`, `src/hooks/__tests__/useHistorico.test.tsx`, `src/test/acessibilidade.test.tsx`, `src/utils/__tests__/graficos.test.ts`
- Modificados: `frontend/eslint.config.js`, `package.json`, `pnpm-lock.yaml`

### 📝 docs: atualiza documentação mkdocs com cobertura de testes atual
- Modificados: `docs/frontend.md`, `docs/index.md`, `docs/setup.md`

### 📝 docs: atualiza README com contagem de testes e requisito pnpm
- Modificados: `README.md`

### ✏️ fix: substitui valor padrão 'admin' por placeholder em WAHA_DASHBOARD_USERNAME
- Modificados: `.env.example`

### 🔧 config: atualiza .env.example com variáveis ausentes
- Modificados: `.env.example`

---

## [1.4.0] — 2026-03-25 a 2026-03-27

### ✨ feat: implementa sistema completo de auditoria e log de acesso
- Novos: `backend/financas/middleware.py`, `migrations/0002_log_auditoria.py`, `migrations/0003_log_acesso.py`, `financas/signals.py`, `tests/test_bulk.py`, `tests/test_middleware.py`, `tests/test_signals.py`
- Modificados: `backend/config/settings.py`, `financas/admin.py`, `financas/apps.py`, `financas/models.py`

### 🐛 fix: adiciona bulk_deletado e bulk_atualizado nas choices de LogAuditoria
- Modificados: `backend/financas/models.py`

### ✅ test: cobertura completa de signals e bulk para todos os models
- Modificados: `backend/financas/tests/test_bulk.py`, `test_signals.py`

### ✅ test: melhora cobertura do middleware de acesso
- Modificados: `backend/financas/middleware.py`, `tests/test_middleware.py`

### ✅ test: adiciona testes de integração e edge cases de auditoria
- Novos: `backend/financas/tests/test_auditoria_integracao.py`

### 🐳 chore: adiciona serviço WAHA ao docker-compose
- Modificados: `.gitignore`, `docker-compose.yml`

### ✨ feat: adiciona app whatsapp com SessaoConversa auditavel
- Novos: `backend/whatsapp/__init__.py`, `apps.py`, `migrations/0001_initial.py`, `models.py`, `signals.py`
- Modificados: `backend/config/settings.py`

### ✨ feat: adiciona webhook e serviço de bot com menu de conversa
- Novos: `backend/whatsapp/services.py`, `whatsapp/urls.py`, `whatsapp/views.py`
- Modificados: `backend/config/urls.py`

### ✨ feat: adiciona admin readonly para SessaoConversa
- Novos: `backend/whatsapp/admin.py`

### ✅ test: cobertura completa do app whatsapp (signals, webhook, fluxo)
- Novos: `backend/whatsapp/tests/__init__.py`, `tests/test_fluxo_conversa.py`, `tests/test_signals_whatsapp.py`, `tests/test_webhook.py`

### ✨ feat: muda trigger do menu para comando explícito e trata erro de envio
- Modificados: `backend/whatsapp/services.py`, `whatsapp/views.py`

### ✅ test: amplia cobertura com comandos desconhecidos, menu e erros de envio
- Modificados: `backend/pyproject.toml`, `uv.lock`, `whatsapp/tests/test_fluxo_conversa.py`, `test_webhook.py`

### ✨ feat: adiciona rate limit de mensagens simultâneas no bot
- Novos: `backend/whatsapp/tests/test_rate_limit.py`
- Modificados: `backend/whatsapp/services.py`

### 🐳 docker: passa vars WAHA ao backend e ativa evento message.any
- Modificados: `docker-compose.yml`

### 🔒 fix: remove autenticação por api key e previne loop de echo no webhook
- Modificados: `backend/whatsapp/views.py`

### ✨ feat: adiciona PREFIXO_BOT para identificar respostas do bot
- Modificados: `backend/whatsapp/services.py`

### ✅ test: amplia cobertura do webhook com filtros de grupo e echo
- Modificados: `backend/whatsapp/tests/test_webhook.py`

### ✨ feat: normaliza corpo da mensagem antes de processar comandos
- Modificados: `backend/whatsapp/services.py`, `tests/test_fluxo_conversa.py`

### ✨ feat: valida e converte valores monetários no formato brasileiro
- Novos: `backend/whatsapp/tests/test_parse_valor.py`
- Modificados: `backend/whatsapp/services.py`, `tests/test_fluxo_conversa.py`

### ✅ test: prova que espaços em valores monetários são ignorados
- Modificados: `backend/whatsapp/tests/test_fluxo_conversa.py`

### ✨ feat: adiciona timeout de inatividade de 5 minutos na sessão
- Novos: `backend/whatsapp/tests/test_timeout.py`
- Modificados: `backend/whatsapp/services.py`

### ✅ test: divide e documenta testes do app financas
- Novos: `backend/financas/tests/test_bulk_entrada_categoria_fonte.py`, `test_signals_categoria_fonte_user.py`, `test_view_entrada_isolamento.py`, `test_view_gasto_isolamento.py`
- Modificados: `backend/financas/tests/test_auditoria_integracao.py`, `test_bulk.py`, `test_middleware.py`, `test_model_*.py`, `test_signals.py`, `test_view_*.py` (múltiplos)

### ✅ test: divide e documenta testes do app whatsapp
- Novos: `backend/whatsapp/tests/test_fluxo_entrada_resumo.py`, `test_fluxo_gasto.py`, `test_webhook_comportamento.py`
- Modificados: `backend/whatsapp/tests/test_fluxo_conversa.py`, `test_parse_valor.py`, `test_rate_limit.py`, `test_signals_whatsapp.py`, `test_timeout.py`, `test_webhook.py`

### ✅ test: divide e documenta testes do frontend React
- Novos: `frontend/src/context/ContextoAutenticacao.logout.test.tsx`
- Modificados: `frontend/src/components/BarraTopo.test.tsx`, `MenuLateral.test.tsx`, `RotaPrivada.test.tsx`, `formularios/__tests__/*.test.tsx`, `context/ContextoAutenticacao.test.tsx`, `pages/*.test.tsx`, `test/security.test.tsx`, `utils/__tests__/format.test.ts`

### 📝 docs: atualiza mkdocs com integração WhatsApp
- Novos: `docs/whatsapp/bot.md`, `docs/whatsapp/configuracao.md`
- Modificados: `backend/mkdocs.yml`, `docs/index.md`, `docs/setup.md`

### 📝 docs: atualiza README com integração WhatsApp
- Modificados: `README.md`

### 🧹 lint: corrige todas as violações de estilo no backend
- Modificados: `backend/config/urls.py`, `financas/tests/test_signals.py`, `test_signals_categoria_fonte_user.py`, `test_view_categoria.py`, `test_view_entrada_isolamento.py`, `test_view_gasto_isolamento.py`, `whatsapp/services.py`, `whatsapp/tests/test_fluxo_entrada_resumo.py`, `test_fluxo_gasto.py`, `test_webhook_comportamento.py`, `whatsapp/views.py`

---

## [1.3.0] — 2026-03-24

### ♻️ refactor: divide test_models e test_views em arquivos menores
- Novos: `backend/financas/tests/test_model_categoria.py`, `test_model_entrada.py`, `test_model_fonte.py`, `test_model_gasto.py`, `test_view_autenticacao.py`, `test_view_categoria.py`, `test_view_entrada.py`, `test_view_fonte.py`, `test_view_gasto.py`, `test_view_paginacao.py`, `test_view_resumo.py`
- Removidos: `backend/financas/tests/test_models.py`, `test_views.py`

### ♻️ refactor: aplica regras Clean Code de tamanho e responsabilidade
- Novos: `backend/financas/tests/test_view_entrada_crud.py`, `test_view_entrada_filtros.py`, `test_view_gasto_crud.py`, `test_view_gasto_filtros.py`, `frontend/src/components/GraficoCard.tsx`, `components/formularios/FormularioCategoriaFonte.tsx`, `FormularioEntrada.tsx`, `FormularioGasto.tsx`, `Mensagens.tsx`, `estilos.ts`, `components/graficos/GraficoBarrasHorizontais.tsx`, `GraficoEntradasVsGastos.tsx`, `GraficoLinhaTempo.tsx`, `hooks/useHistorico.ts`, `utils/graficos.ts`
- Modificados: `frontend/src/pages/PaginaCadastro.tsx`, `PaginaHistorico.tsx`, `PaginaPainel.tsx`

### 👷 ci: adiciona análise estática de qualidade de código (xenon, check-file-length, ESLint max-lines)
- Novos: `backend/scripts/check_file_length.py`
- Modificados: `backend/.pre-commit-config.yaml`, `pyproject.toml`, `uv.lock`, `frontend/eslint.config.js`

### ♻️ refactor: substitui max-lines-per-function por complexidade ciclomática no frontend
- Modificados: `frontend/eslint.config.js`, `src/pages/PaginaHistorico.tsx`

### 🧹 chore: corrige avisos de ruff apontados pelo pre-commit
- Modificados: `backend/financas/serializers.py`, `tests/test_view_categoria.py`, `scripts/check_file_length.py`

### 🧹 chore: substitui criação manual de Fonte por fixture em test_view_categoria
- Modificados: `backend/financas/tests/test_view_categoria.py`

### 📝 docs: adiciona regra de nomenclatura consistente em português no CLAUDE.md
- Modificados: `CLAUDE.md`

### ✅ test: adiciona testes de formulários e mobile; remove duplicatas
- Novos: `frontend/src/components/formularios/__tests__/FormularioCategoriaFonte.test.tsx`, `FormularioEntrada.test.tsx`, `FormularioGasto.test.tsx`
- Removidos: `frontend/src/components/__tests__/RotaPrivada.test.tsx`, `src/context/__tests__/ContextoAutenticacao.test.tsx`, `src/pages/PaginaCadastro.test.tsx`, `src/pages/PaginaLogin.test.tsx`, `src/pages/__tests__/PaginaHistorico.test.tsx`, `src/pages/__tests__/PaginaPainel.test.tsx`
- Modificados: `frontend/src/components/MenuLateral.test.tsx`

### 🔧 config: desabilita flake8 no VSCode em favor do ruff
- Modificados: `.vscode/settings.json`

### 🧹 chore: aplica formatação automática do ruff nos arquivos do backend
- Modificados: `backend/config/urls.py`, `financas/tests/test_model_*.py`, `test_view_*.py` (múltiplos)

### 📝 docs: atualiza mkdocs com gráficos, layout mobile, testes e pre-commit hooks
- Modificados: `docs/frontend.md`, `docs/index.md`, `docs/setup.md`

### ♻️ refactor: nomenclatura consistente em português
> Renomeia componentes do frontend para português. Inclui temporariamente sge-master (removido no commit seguinte).
- Novos (renomeados): `frontend/src/api/autenticacao.ts`, `components/BarraTopo.tsx`, `components/BarraTopo.test.tsx`, `components/MenuLateral.tsx`, `components/MenuLateral.test.tsx`, `components/RotaPrivada.tsx`, `context/ContextoAutenticacao.tsx`, `context/useAutenticacao.ts`, `pages/PaginaCadastro.tsx`, `pages/PaginaHistorico.tsx`, `pages/PaginaLogin.tsx`, `pages/PaginaPainel.tsx`
- Modificados: `backend/financas/serializers.py`, `views.py`, `frontend/src/App.tsx`, `test/security.test.tsx`, `test/utils.tsx`

### 🔥 chore: remove pasta sge-master do repositório
- Removidos: `sge-master/` (projeto anterior completo — 60+ arquivos)

---

## [1.2.0] — 2026-03-20

### 📱 feat: layout responsivo para mobile
- Modificados: `frontend/src/components/Layout.tsx`, `components/MenuLateral.tsx`, `components/BarraTopo.tsx` (e seus testes)

---

## [1.1.0] — 2026-03-19 a 2026-03-20

### ✨ feat: adiciona frontend React + TypeScript
- Novos: `frontend/` (estrutura completa — Dockerfile, package.json, src/App.tsx, api/, components/, context/, pages/, test/, utils/, tsconfig*.json, vite.config.ts, etc.)
- Modificados: `backend/.env.example`, `backend/config/settings.py`, `docker-compose.yml`, `.vscode/settings.json`

### 🐛 fix: desativa paginação em CategoriaViewSet e FonteViewSet
- Modificados: `backend/financas/views.py`

### ✅ test: regressão da paginação e correções nos testes do backend
- Modificados: `backend/financas/tests/test_views.py`

### 📝 docs: atualiza README e MkDocs para incluir o frontend
- Novos: `docs/frontend.md`
- Modificados: `README.md`, `backend/mkdocs.yml`, `docs/api/endpoints.md`, `docs/index.md`, `docs/setup.md`

### 📝 docs: adiciona regra de Git Emojis (Gitmoji) no CLAUDE.md
- Modificados: `CLAUDE.md`

### 🐛 fix: exibe username real no TopBar e adiciona claims ao JWT
- Modificados: `backend/config/urls.py`, `financas/serializers.py`, `docker-compose.yml`, `frontend/src/components/BarraTopo.tsx`

### 🐛 fix: inclui categoria_nome e fonte_nome nas respostas da API
- Modificados: `backend/financas/serializers.py`

### ✨ feat: adiciona gráficos interativos no Dashboard
- Modificados: `frontend/package.json`, `pnpm-lock.yaml`, `src/api/financas.ts`, `src/pages/PaginaPainel.tsx` (e testes)

---

## [1.0.0] — 2026-03-17 ⚠️ Breaking Change

> **Migração SQLite → PostgreSQL via Docker.** Ambientes sem Docker precisam ser reconfigurados.

### 🐘 feat: substitui SQLite por PostgreSQL via Docker
- Novos: `docker-compose.yml`
- Modificados: `backend/.env.example`, `backend/config/settings.py`

### 🧪 test: remove skip do CheckConstraint agora que usamos PostgreSQL
- Modificados: `backend/financas/tests/test_models.py`

### 🐳 feat: dockeriza o backend Django
- Novos: `backend/.dockerignore`, `backend/Dockerfile`
- Modificados: `docker-compose.yml`

### 🐳 refactor: Dockerfile com python:3.14-slim e credenciais via .env
- Novos: `.env.example`
- Modificados: `backend/Dockerfile`, `docker-compose.yml`

### 📝 docs: atualiza README e MkDocs para stack com Docker e Python 3.14
- Modificados: `README.md`, `docs/index.md`, `docs/setup.md`

---

## [0.3.0] — 2026-03-16

### 📝 docs: configura MkDocs e atualiza README
- Novos: `docs/api/autenticacao.md`, `docs/api/endpoints.md`, `docs/api/resumo.md`, `docs/index.md`, `docs/modelos/categoria.md`, `docs/modelos/entrada.md`, `docs/modelos/fonte.md`, `docs/modelos/gasto.md`, `docs/setup.md`
- Modificados: `.gitignore`, `README.md`, `backend/mkdocs.yml`

### ♻️ refactor: extrai CamposImutaveisMixin e adiciona usuario aos models
- Modificados: `backend/config/settings.py`, `financas/migrations/0001_initial.py`, `financas/models.py`, `manage.py`, `pyproject.toml`

### ✨ feat: isolamento multi-usuário em views, serializers e admin
- Modificados: `backend/financas/admin.py`, `financas/serializers.py`, `financas/views.py`

### 🧪 test: atualiza test_models e reescreve test_views com isolamento
- Modificados: `backend/financas/tests/test_models.py`, `test_views.py`

### 📝 docs: atualiza MkDocs para refletir isolamento multi-usuário
- Modificados: `docs/api/endpoints.md`, `docs/api/resumo.md`, `docs/modelos/*.md`

---

## [0.2.0] — 2026-03-16

### ✨ feat: cria app financas com models Categoria, Fonte, Gasto e Entrada
- Novos: `backend/financas/__init__.py`, `admin.py`, `apps.py`, `migrations/0001_initial.py`, `migrations/__init__.py`, `models.py`, `validators.py`, `views.py`

### 🧪 test: adiciona testes TDD para os 4 models do app financas
- Novos: `backend/financas/tests/__init__.py`, `tests/test_models.py`

### ✨ feat: cria app financas com models, serializers, views e urls
- Novos: `backend/financas/serializers.py`, `financas/urls.py`
- Modificados: `backend/financas/views.py`

### 🧪 test: adiciona testes TDD para os endpoints do app financas
- Novos: `backend/financas/tests/test_views.py`
- Modificados: `backend/.pre-commit-config.yaml`, `backend/config/urls.py`, `backend/pyproject.toml`

### 🧪 test: expande cobertura dos endpoints com testes de validação e PATCH
- Modificados: `backend/financas/tests/test_views.py`, `backend/pyproject.toml`

### ✨ feat: adiciona read_only, type hints, filtros, paginação e resumo
- Modificados: `backend/config/settings.py`, `financas/serializers.py`, `financas/urls.py`, `financas/views.py`

### 🧪 test: adiciona testes de filtros, paginação e endpoint de resumo
- Modificados: `backend/financas/tests/test_views.py`

---

## [0.1.0] — 2026-03-09 a 2026-03-16

### 🎉 Initial commit
- Novos: `LICENSE`

### 🎉 First Commit
- Novos: `.gitignore`, `.python-version`, `main.py`, `pyproject.toml`

### 🏗️ feat: setup inicial da infraestrutura e blindagem do backend
- Novos: `README.md`, `backend/.pre-commit-config.yaml`, `backend/docs/index.md`, `backend/mkdocs.yml`, `backend/pyproject.toml`, `backend/uv.lock`, `settings.json`
- Modificados (movidos): `.python-version → backend/.python-version`, `main.py → backend/main.py`
- Removidos: `pyproject.toml` (raiz)

### 🔧 chore: corrige tooling, dependências e configuração de testes
- Novos: `CLAUDE.md`
- Modificados: `backend/.pre-commit-config.yaml`, `backend/pyproject.toml`

### 📝 docs: reescreve README com markdown limpo e visão geral do projeto
- Modificados: `README.md`

### 🔒 chore: atualiza .gitignore e adiciona .env.example
- Novos: `backend/.env.example`
- Modificados: `.gitignore`

### 🏗️ feat: inicializa projeto Django e configura settings por ambiente
- Novos: `backend/config/__init__.py`, `config/asgi.py`, `config/settings/__init__.py`, `config/settings/base.py`, `config/settings/dev.py`, `config/settings/prod.py`, `config/urls.py`, `config/wsgi.py`, `backend/manage.py`
- Removidos: `backend/main.py`
- Modificados: `backend/.pre-commit-config.yaml`

### 📦 chore: atualiza dependências e configuração do pytest
- Modificados: `backend/pyproject.toml`, `backend/uv.lock`

### 🧹 refactor: consolida settings em arquivo único e atualiza Ruff
- Novos (renomeado): `backend/config/settings.py`
- Removidos: `backend/config/settings/__init__.py`, `settings/dev.py`, `settings/prod.py`
- Modificados: `backend/config/asgi.py`, `config/wsgi.py`, `backend/pyproject.toml`
