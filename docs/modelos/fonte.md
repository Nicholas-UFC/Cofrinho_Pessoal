# Fonte

Representa a origem de uma entrada de dinheiro (ex: Salário, Freelance, Investimentos).

## Campos

| Campo       | Tipo              | Descrição                              |
|-------------|-------------------|----------------------------------------|
| `id`        | inteiro           | Identificador único (gerado automaticamente) |
| `nome`      | texto (100 chars) | Nome da fonte — deve ser único         |
| `criado_em` | datetime          | Data de criação (somente leitura)      |

## Regras

- `nome` é obrigatório e único — não existem duas fontes com o mesmo nome.
- `criado_em` é preenchido automaticamente na criação e não pode ser alterado.
- Não é possível excluir uma fonte que possui entradas vinculadas
  (`PROTECT` — retorna erro `403`).

## Exemplo

```json
{
  "id": 1,
  "nome": "Salário",
  "criado_em": "2026-03-16T10:00:00-03:00"
}
```
