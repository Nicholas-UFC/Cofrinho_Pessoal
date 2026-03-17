# Gasto

Registra uma saída de dinheiro vinculada a uma categoria.

## Campos

| Campo        | Tipo              | Descrição                                          |
|--------------|-------------------|----------------------------------------------------|
| `id`         | inteiro           | Identificador único (gerado automaticamente)       |
| `descricao`  | texto (200 chars) | Descrição do gasto                                 |
| `valor`      | decimal (10, 2)   | Valor do gasto — deve ser maior que zero           |
| `categoria`  | FK → Categoria    | Categoria do gasto (obrigatória)                   |
| `data`       | date              | Data em que o gasto ocorreu                        |
| `criado_em`  | datetime          | Data de criação (somente leitura)                  |

> O campo `usuario` existe no banco de dados mas **não é exposto pela API**.
> Ele é preenchido automaticamente a partir do token JWT.

## Regras

- `valor` deve ser maior que zero — valores negativos ou zero retornam erro `400`.
- `categoria` é obrigatória — um gasto sem categoria retorna erro `400`.
- `criado_em` é preenchido automaticamente e não pode ser alterado via API.
- A listagem padrão é ordenada pela `data` mais recente primeiro.
- A API retorna apenas os gastos do usuário autenticado.

## Exemplo de resposta

```json
{
  "id": 1,
  "descricao": "Supermercado",
  "valor": "150.00",
  "categoria": 1,
  "data": "2026-03-16",
  "criado_em": "2026-03-16T10:00:00-03:00"
}
```
