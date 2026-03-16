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

## 5. Coding Standard (Estilo do Usuario)

- Refatorar sempre que o usuario pedir, sem resistencia.
- Seguir as convencoes de codigo ja existentes no projeto (Ruff, Bandit, pre-commit).
- Nao adicionar complexidade desnecessaria — minimalismo e preferido.
