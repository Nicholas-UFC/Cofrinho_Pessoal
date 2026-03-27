# Configuração do WhatsApp

## Pré-requisitos

O bot utiliza o **WAHA** (WhatsApp HTTP API), um servidor que conecta o
WhatsApp ao backend via webhook. O container WAHA já está incluído no
`docker-compose.yml` do projeto.

## Variáveis de ambiente

Adicione as seguintes variáveis ao `.env` antes de subir os containers:

```env
# URL interna do WAHA (comunicação entre containers)
WAHA_API_URL=http://waha:3000

# Chave de autenticação — deve ser a mesma em WAHA_API_KEY e WHATSAPP_API_KEY
WAHA_API_KEY=sua-chave-aqui

# ID do grupo WhatsApp que o bot vai monitorar
# Formato: número@g.us (ex: 120363423218993414@g.us)
WAHA_GROUP_ID=120363423218993414@g.us

# Nome da sessão WAHA (pode deixar "default")
WAHA_SESSION=default

# Username Django do dono da conta (os gastos/entradas serão vinculados a ele)
WAHA_OWNER_USERNAME=seu_usuario_django

# Credenciais do painel web do WAHA (http://localhost:3000)
WAHA_DASHBOARD_USERNAME=admin
WAHA_DASHBOARD_PASSWORD=senha-segura
```

## Passo a passo para ativar

**1. Suba os containers:**

```bash
docker compose up -d
```

**2. Acesse o painel WAHA:**

Abra <http://localhost:3000> no navegador. Faça login com
`WAHA_DASHBOARD_USERNAME` e `WAHA_DASHBOARD_PASSWORD`.

**3. Inicie a sessão e escaneie o QR code:**

No painel, clique em **Start** na sessão `default`. Um QR code será exibido.
Abra o WhatsApp no celular, vá em **Dispositivos conectados** e escaneie o
código.

**4. Obtenha o ID do grupo:**

Após conectar, envie qualquer mensagem no grupo que o bot vai monitorar.
O WAHA registrará o evento. O ID do grupo aparece no campo `from` do payload
— formato `123456789@g.us`. Copie esse valor para `WAHA_GROUP_ID` no `.env`
e reinicie o backend:

```bash
docker compose restart backend
```

**5. Teste o bot:**

Envie `menu` no grupo configurado. O bot deve responder com o menu principal.

## Como o webhook é registrado

O WAHA envia eventos para o backend automaticamente via a variável
`WHATSAPP_HOOK_URL` definida no `docker-compose.yml`:

```
http://backend:8000/api/whatsapp/webhook/
```

O evento configurado é `message.any`, que cobre tanto mensagens recebidas
quanto enviadas (necessário para o bot ignorar seu próprio echo).

## Verificação

Para confirmar que tudo está funcionando, monitore os logs do backend:

```bash
docker compose logs -f backend
```

Ao enviar uma mensagem no grupo, você verá o processamento da requisição
de webhook nos logs.
