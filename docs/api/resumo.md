# Endpoint de Resumo

Retorna um panorama financeiro consolidado: saldo, totais e gastos
agrupados por categoria.

## Requisição

```http
GET /api/financas/resumo/
Authorization: Bearer {token}
```

## Resposta

```json
{
  "total_entradas": "5000.00",
  "total_gastos": "1850.00",
  "saldo": "3150.00",
  "gastos_por_categoria": [
    {
      "categoria__nome": "Alimentação",
      "total": "850.00"
    },
    {
      "categoria__nome": "Transporte",
      "total": "300.00"
    },
    {
      "categoria__nome": "Moradia",
      "total": "700.00"
    }
  ]
}
```

## Campos

| Campo                  | Descrição                                        |
|------------------------|--------------------------------------------------|
| `total_entradas`       | Soma de todas as entradas registradas            |
| `total_gastos`         | Soma de todos os gastos registrados              |
| `saldo`                | `total_entradas - total_gastos`                  |
| `gastos_por_categoria` | Lista com o total gasto em cada categoria, ordenada alfabeticamente |

## Observações

- Quando não há registros, os totais retornam `0` (não `null`).
- O endpoint não filtra por período — considera todos os registros.
- A lista `gastos_por_categoria` é ordenada pelo nome da categoria.
