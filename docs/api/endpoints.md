# Endpoints

Todos os endpoints exigem autenticação JWT. A base da URL é `/api/financas/`.

## Isolamento multi-usuário

Todos os endpoints aplicam isolamento automático por usuário:

- A listagem retorna **apenas os dados do usuário autenticado**.
- Tentar acessar, editar ou deletar um recurso de outro usuário retorna **`404`**.
- O campo `usuario` nunca aparece na requisição nem na resposta — ele é definido
  automaticamente pelo servidor a partir do token JWT.

## Categorias

| Método   | URL                     | Descrição                  |
|----------|-------------------------|----------------------------|
| `GET`    | `/categorias/`          | Lista todas as categorias  |
| `POST`   | `/categorias/`          | Cria uma categoria         |
| `GET`    | `/categorias/{id}/`     | Detalhe de uma categoria   |
| `PUT`    | `/categorias/{id}/`     | Atualização completa       |
| `PATCH`  | `/categorias/{id}/`     | Atualização parcial        |
| `DELETE` | `/categorias/{id}/`     | Remove uma categoria       |

## Fontes

| Método   | URL                 | Descrição              |
|----------|---------------------|------------------------|
| `GET`    | `/fontes/`          | Lista todas as fontes  |
| `POST`   | `/fontes/`          | Cria uma fonte         |
| `GET`    | `/fontes/{id}/`     | Detalhe de uma fonte   |
| `PUT`    | `/fontes/{id}/`     | Atualização completa   |
| `PATCH`  | `/fontes/{id}/`     | Atualização parcial    |
| `DELETE` | `/fontes/{id}/`     | Remove uma fonte       |

## Gastos

| Método   | URL                 | Descrição            |
|----------|---------------------|----------------------|
| `GET`    | `/gastos/`          | Lista todos os gastos |
| `POST`   | `/gastos/`          | Registra um gasto    |
| `GET`    | `/gastos/{id}/`     | Detalhe de um gasto  |
| `PUT`    | `/gastos/{id}/`     | Atualização completa |
| `PATCH`  | `/gastos/{id}/`     | Atualização parcial  |
| `DELETE` | `/gastos/{id}/`     | Remove um gasto      |

### Filtros disponíveis para Gastos

| Parâmetro      | Exemplo                        | Descrição                  |
|----------------|--------------------------------|----------------------------|
| `categoria`    | `?categoria=1`                 | Filtra por ID de categoria |
| `data`         | `?data=2026-03-16`             | Data exata                 |
| `data__gte`    | `?data__gte=2026-03-01`        | A partir de uma data       |
| `data__lte`    | `?data__lte=2026-03-31`        | Até uma data               |
| `valor__gte`   | `?valor__gte=100`              | Valor mínimo               |
| `valor__lte`   | `?valor__lte=500`              | Valor máximo               |

## Entradas

| Método   | URL                   | Descrição               |
|----------|-----------------------|-------------------------|
| `GET`    | `/entradas/`          | Lista todas as entradas |
| `POST`   | `/entradas/`          | Registra uma entrada    |
| `GET`    | `/entradas/{id}/`     | Detalhe de uma entrada  |
| `PUT`    | `/entradas/{id}/`     | Atualização completa    |
| `PATCH`  | `/entradas/{id}/`     | Atualização parcial     |
| `DELETE` | `/entradas/{id}/`     | Remove uma entrada      |

### Filtros disponíveis para Entradas

| Parâmetro    | Exemplo                  | Descrição              |
|--------------|--------------------------|------------------------|
| `fonte`      | `?fonte=1`               | Filtra por ID de fonte |
| `data`       | `?data=2026-03-16`       | Data exata             |
| `data__gte`  | `?data__gte=2026-03-01`  | A partir de uma data   |
| `data__lte`  | `?data__lte=2026-03-31`  | Até uma data           |
| `valor__gte` | `?valor__gte=1000`       | Valor mínimo           |
| `valor__lte` | `?valor__lte=5000`       | Valor máximo           |

## Paginação

Todas as listagens retornam no formato paginado com **20 itens por página**:

```json
{
  "count": 42,
  "next": "http://localhost:8000/api/financas/gastos/?page=2",
  "previous": null,
  "results": [...]
}
```

Use `?page=2` para navegar entre as páginas.
