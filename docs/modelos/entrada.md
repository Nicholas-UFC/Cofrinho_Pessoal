# Entrada

Registra um recebimento de dinheiro vinculado a uma fonte de renda.

## Campos

| Campo       | Tipo              | Descrição                                          |
|-------------|-------------------|----------------------------------------------------|
| `id`        | inteiro           | Identificador único (gerado automaticamente)       |
| `descricao` | texto (200 chars) | Descrição da entrada                               |
| `valor`     | decimal (10, 2)   | Valor recebido — deve ser maior que zero           |
| `fonte`     | FK → Fonte        | Fonte da entrada (obrigatória)                     |
| `data`      | date              | Data em que o valor foi recebido                   |
| `criado_em` | datetime          | Data de criação (somente leitura)                  |

> O campo `usuario` existe no banco de dados mas **não é exposto pela API**.
> Ele é preenchido automaticamente a partir do token JWT.

## Regras

- `valor` deve ser maior que zero — valores negativos ou zero retornam erro `400`.
- `fonte` é obrigatória — uma entrada sem fonte retorna erro `400`.
- `criado_em` é preenchido automaticamente e não pode ser alterado via API.
- A listagem padrão é ordenada pela `data` mais recente primeiro.
- A API retorna apenas as entradas do usuário autenticado.

## Exemplo de resposta

```json
{
  "id": 1,
  "descricao": "Salário Janeiro",
  "valor": "3000.00",
  "fonte": 1,
  "data": "2026-03-05",
  "criado_em": "2026-03-05T09:00:00-03:00"
}
```
