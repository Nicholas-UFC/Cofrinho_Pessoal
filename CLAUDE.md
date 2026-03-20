# Regras de Desenvolvimento — Cofrinho Pessoal

Este projeto adota **Extreme Programming** como metodologia de vibe-coding. As regras abaixo devem ser seguidas em toda conversa.

## 1. Pair Programming (Planejar Antes de Executar)

- Antes de qualquer implementacao, apresentar um **plano detalhado** de tudo o que sera feito.
- Aguardar a **aprovacao explicita** do usuario antes de comecar a executar.
- Ao final, ajustar o que o usuario apontar como faltante ou errado.

## 2. Test-Driven Development (TDD)

- Toda nova funcionalidade deve ser acompanhada de **testes unitarios**.
- Toda correcao de bug deve vir com um **teste de regressao** que reproduz o problema.
- Nunca fazer commit de funcionalidade sem testes correspondentes.

## 3. Continuous Integration (CI)

- Apos cada implementacao, rodar o script de CI para verificar que nada quebrou.
- O branch `main` **so recebe commits com testes passando**.
- O projeto deve poder ser revertido a qualquer commit e continuar funcionando.

## 4. Small Releases (Commits Atomicos)

- Nunca usar `git add .` indiscriminadamente.
- Cada tarefa gera seu **proprio commit**, com descricao clara e precisa.
- Se multiplas tarefas forem feitas antes do commit, separar em commits distintos.

## 5. Git Emojis (Gitmoji)

- Todo commit deve comecar com um emoji Gitmoji antes do tipo convencional.
- Formato obrigatorio: `<emoji> <tipo>: <descricao>`
- Referencia completa em: [https://gitmoji.dev](https://gitmoji.dev)

Emojis disponiveis:

| Emoji | Uso |
| ----- | --- |
| ✨ | Nova funcionalidade |
| 🐛 | Correcao de bug |
| 🚑 | Hotfix critico |
| 📝 | Documentacao |
| 🎨 | Melhoria de estrutura/formato do codigo |
| ⚡ | Melhoria de performance |
| 🔥 | Remocao de codigo ou arquivos |
| 🚀 | Deploy |
| ✅ | Adicao ou correcao de testes |
| 🔒 | Correcao de vulnerabilidade de seguranca |
| 🔑 | Segredos ou chaves |
| 🔖 | Tag de versao/release |
| ♻️ | Refatoracao |
| ➕ | Adicao de dependencia |
| ➖ | Remocao de dependencia |
| 🐳 | Docker / infraestrutura |
| 🔧 | Configuracao (arquivos de config) |
| 🔨 | Scripts de build ou desenvolvimento |
| 🌐 | Internacionalizacao / traducao |
| ✏️ | Correcao de typo |
| 💄 | UI / estilo visual |
| 🎉 | Commit inicial |
| 🚧 | Work in progress |
| 💚 | Correcao de CI |
| ⬆️ | Upgrade de dependencia |
| ⬇️ | Downgrade de dependencia |
| 📌 | Fixar versao de dependencia |
| 👷 | Adicao ou atualizacao de CI |
| 💡 | Adicao de comentarios no codigo |
| 🔀 | Merge de branches |
| 📦 | Arquivos compilados ou pacotes |
| 👽 | Atualizacao por mudanca em API externa |
| 🍱 | Assets (imagens, fontes, etc.) |
| ♿ | Acessibilidade |
| 🗃️ | Mudancas relacionadas a banco de dados |
| 🔊 | Adicao de logs |
| 🔇 | Remocao de logs |
| 👥 | Contribuidores |
| 🏗️ | Mudancas arquiteturais |
| 🤡 | Mocks / stubs para testes |
| 🥚 | Easter egg |
| 🙈 | Atualizacao de .gitignore |
| 📸 | Snapshots de testes |
| ⚗️ | Experimento / prova de conceito |
| 🔍 | SEO |
| 🏷️ | Tipos (TypeScript, type hints) |
| 🌱 | Dados iniciais (seed) |
| 🚩 | Feature flags |
| 🥅 | Tratamento de erros |
| 💫 | Animacoes / transicoes |
| 🗑️ | Deprecacao de codigo |
| 🛂 | Autorizacao / autenticacao / permissoes |
| 🩺 | Health check |
| 🧱 | Mudancas de infraestrutura |
| 🧪 | Testes falhando (esperado) |
| 👔 | Logica de negocio |
| 🩹 | Fix simples / nao critico |
| 🧹 | Limpeza de codigo (lint, formatacao) |

## 6. Coding Standard (Estilo do Usuario)

- Refatorar sempre que o usuario pedir, sem resistencia.
- Seguir as convencoes de codigo ja existentes no projeto (Ruff, Bandit, pre-commit).
- Nao adicionar complexidade desnecessaria — minimalismo e preferido.
