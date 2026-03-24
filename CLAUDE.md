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

## 7. Clean Code (Tamanho e Responsabilidade)

Baseado no livro Clean Code de Robert C. Martin. Estas regras se aplicam a todo codigo do projeto.

### Tamanho de arquivos

- **Ideal: 200-300 linhas** — suficiente para conter uma unica responsabilidade.
- **Maximo toleravel: 500 linhas** — acima disso e sinal de que o arquivo faz coisas demais.
- Quando um arquivo ultrapassar 500 linhas, dividi-lo em modulos menores antes de continuar.

### Tamanho de funcoes e metodos

- **Ideal: 5-10 linhas** — funcoes curtas sao mais faceis de testar e entender.
- **Maximo: 20 linhas** — funcoes longas devem ser quebradas em funcoes menores com nomes descritivos.
- Regra de ouro: **uma funcao deve fazer uma unica coisa, e faze-la bem**.
- Se um bloco de codigo precisar de comentario para ser entendido, extraia-o para uma funcao com nome claro.

### Responsabilidade de classes

- Cada classe deve ter **uma unica razao para mudar** (SRP — Single Responsibility Principle).
- Quanto mais variaveis de instancia, mais a classe provavelmente esta fazendo coisas demais.
- Metodos devem ser pequenos e coesos entre si.

### Regra do escoteiro

> "Deixe o codigo mais limpo do que voce encontrou."

Ao editar qualquer arquivo, corrija pequenas sujeiras que estiver vendo (nomes ruins, funcoes longas, codigo duplicado) — mesmo que nao sejam o foco da tarefa.
