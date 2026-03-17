# Autenticação

A API usa **JWT (JSON Web Token)** via SimpleJWT. Todo endpoint (exceto
`/api/token/`) exige um token válido no cabeçalho da requisição.

## Obter token

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
  "access": "eyJ0eXAiOiJKV1QiLCJhbGci...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGci..."
}
```

- **access** — token de acesso, válido por **1 hora**
- **refresh** — token de renovação, válido por **7 dias**

## Usar o token

Inclua o token de acesso no cabeçalho `Authorization`:

```http
GET /api/financas/gastos/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGci...
```

## Renovar token

Quando o `access` expirar, use o `refresh` para obter um novo:

```http
POST /api/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGci..."
}
```

A cada renovação, um novo `refresh` é gerado (`ROTATE_REFRESH_TOKENS=True`).

## Erros comuns

| Código | Significado |
|--------|-------------|
| `401`  | Token ausente ou inválido |
| `401`  | Token expirado |
| `403`  | Sem permissão para o recurso |
