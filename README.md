# Cofrinho Pessoal

Aplicação pessoal para controle de gastos. Registre despesas via WhatsApp, app mobile ou navegador — com categorização automática por IA.

---

## Como funciona

Você envia uma mensagem no WhatsApp (ex: *"gastei 45 reais no mercado"*), a IA categoriza automaticamente e o gasto é registrado. O mesmo pode ser feito pelo app mobile ou pela interface web.

---

## Stack

| Camada | Tecnologia |
| --- | --- |
| Backend | Django 6 + Django REST Framework |
| Banco de Dados | PostgreSQL |
| Autenticação | JWT (SimpleJWT) |
| IA | Google Gemini |
| WhatsApp | WAHA Gateway |
| Frontend Web | React |
| App Mobile | React Native |
| Infra | Docker + Nginx |

---

## Arquitetura

```text
Clientes (WhatsApp / App / Web)
        │
        ▼
   Nginx (proxy reverso)
        │
   ┌────┴────┐
   │         │
React     Django REST ◄──► Gemini AI
               │
           PostgreSQL
```

O WhatsApp entra via WAHA Gateway direto no Django. Os demais clientes passam pelo Nginx.

---

## Licença

[GNU AGPL v3.0](LICENSE)
