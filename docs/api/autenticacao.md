# Autenticação

A API usa **JWT (JSON Web Token)** via SimpleJWT. Os tokens são armazenados em
**cookies httpOnly** — nunca expostos ao JavaScript — o que elimina a superfície
de ataque de XSS.

Todo endpoint (exceto `/api/token/` e `/api/token/refresh/`) exige um cookie de
acesso válido.

## Login

```http
POST /api/token/
Content-Type: application/json

{
  "username": "seu_usuario",
  "password": "sua_senha"
}
```

**Resposta:**

```json
{
  "username": "seu_usuario",
  "is_staff": false
}
```

Os tokens **não aparecem no corpo da resposta**. O servidor seta dois cookies
httpOnly automaticamente:

| Cookie          | Conteúdo        | Validade |
|-----------------|-----------------|----------|
| `access`        | Token de acesso | 1 hora   |
| `refresh`       | Token de refresh| 7 dias   |

## Requisições autenticadas

Nenhum cabeçalho extra é necessário. O browser envia os cookies automaticamente.
Em chamadas via código (ex: axios), use `withCredentials: true`:

```ts
axios.get("/api/financas/gastos/", { withCredentials: true });
```

## Renovar token

Quando o cookie `access` expirar, envie uma requisição para renovação — o cookie
`refresh` é lido automaticamente pelo servidor:

```http
POST /api/token/refresh/
```

**Resposta:** novo cookie `access` é setado. Um novo `refresh` também é gerado
(`ROTATE_REFRESH_TOKENS=True`).

## Logout

```http
POST /api/logout/
```

O servidor blacklista o `refresh` token e limpa ambos os cookies. Após o logout,
requisições com os cookies antigos retornam `401`.

## Erros comuns

| Código | Significado                          |
|--------|--------------------------------------|
| `401`  | Cookie ausente, inválido ou expirado |
| `403`  | Sem permissão para o recurso         |
