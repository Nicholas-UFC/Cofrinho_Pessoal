# Categoria

Agrupa os gastos por tipo (ex: Alimentação, Transporte, Moradia).

## Campos

| Campo       | Tipo             | Descrição                                          |
|-------------|------------------|----------------------------------------------------|
| `id`        | inteiro          | Identificador único (gerado automaticamente)       |
| `nome`      | texto (100 chars)| Nome da categoria                                  |
| `criado_em` | datetime         | Data de criação (somente leitura)                  |

> O campo `usuario` existe no banco de dados mas **não é exposto pela API**.
> Ele é preenchido automaticamente a partir do token JWT.

## Regras

- `nome` é obrigatório e único **por usuário** — dois usuários diferentes podem ter
  uma categoria com o mesmo nome, mas o mesmo usuário não pode ter duplicatas.
- `criado_em` é preenchido automaticamente na criação e não pode ser alterado.
- Não é possível excluir uma categoria que possui gastos vinculados
  (`PROTECT` — retorna erro `403`).
- A API retorna apenas as categorias do usuário autenticado.

## Exemplo de resposta

```json
{
  "id": 1,
  "nome": "Alimentação",
  "criado_em": "2026-03-16T10:00:00-03:00"
}
```
