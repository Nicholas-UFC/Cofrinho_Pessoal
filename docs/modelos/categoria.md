# Categoria

Agrupa os gastos por tipo (ex: Alimentação, Transporte, Moradia).

## Campos

| Campo       | Tipo             | Descrição                              |
|-------------|------------------|----------------------------------------|
| `id`        | inteiro          | Identificador único (gerado automaticamente) |
| `nome`      | texto (100 chars)| Nome da categoria — deve ser único     |
| `criado_em` | datetime         | Data de criação (somente leitura)      |

## Regras

- `nome` é obrigatório e único — não existem duas categorias com o mesmo nome.
- `criado_em` é preenchido automaticamente na criação e não pode ser alterado.
- Não é possível excluir uma categoria que possui gastos vinculados
  (`PROTECT` — retorna erro `403`).

## Exemplo

```json
{
  "id": 1,
  "nome": "Alimentação",
  "criado_em": "2026-03-16T10:00:00-03:00"
}
```
