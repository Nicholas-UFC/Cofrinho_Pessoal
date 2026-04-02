# Bot para WhatsApp

O Cofrinho Pessoal possui um bot que permite registrar, editar, excluir e
listar gastos e entradas, além de consultar o resumo financeiro do mês,
diretamente pelo WhatsApp, sem precisar abrir o navegador.

## Como funciona

O bot monitora mensagens de um grupo específico do WhatsApp via **WAHA**
(WhatsApp HTTP API). Quando uma mensagem chega, o webhook do Django processa
o conteúdo e responde de volta no mesmo grupo.

O bot é orientado por **estados de sessão** — cada grupo tem uma
`SessaoConversa` no banco que registra em que etapa do fluxo o usuário está.
Isso permite uma conversa multi-turno natural, como um formulário guiado por
mensagens.

```
Usuário → WhatsApp → WAHA → Webhook Django → processar_mensagem() → WAHA → WhatsApp → Usuário
```

## Comandos disponíveis

| Mensagem | Ação                                          |
|----------|-----------------------------------------------|
| `menu`   | Exibe o menu principal                        |
| `1`      | Inicia o fluxo de registro de gasto           |
| `2`      | Inicia o fluxo de registro de entrada         |
| `3`      | Exibe o resumo financeiro do mês atual        |
| `4`      | Gerenciar gastos (listar, editar, excluir)    |
| `5`      | Gerenciar entradas (listar, editar, excluir)  |
| `0`      | Cancela qualquer operação em andamento        |
| `v`      | Volta um passo no fluxo atual                 |
| `s`      | Confirma a operação pendente                  |
| `n`      | Cancela a operação pendente                   |

## Fluxo de registro de gasto

```
[menu] → 1
  → "Qual o valor do gasto?"
  → usuário digita: 25,50
  → "Qual a categoria?" (lista numerada)
  → usuário digita: 2
  → "Confirma? Valor: R$ 25.50 | Categoria: Alimentação"
  → usuário digita: s
  → ✅ Gasto registrado com sucesso!
```

## Fluxo de registro de entrada

```
[menu] → 2
  → "Qual o valor da entrada?"
  → usuário digita: 3.000,00
  → "Qual a fonte?" (lista numerada)
  → usuário digita: 1
  → "Confirma? Valor: R$ 3000.00 | Fonte: Salário"
  → usuário digita: s
  → ✅ Entrada registrada com sucesso!
```

## Formato de valores aceitos

O bot aceita valores nos formatos brasileiros mais comuns:

| Formato    | Exemplo      | Interpretado como |
|------------|--------------|-------------------|
| Inteiro    | `25`         | R$ 25,00          |
| Decimal    | `25,50`      | R$ 25,50          |
| Milhar     | `1.500`      | R$ 1.500,00       |
| Combinado  | `1.500,00`   | R$ 1.500,00       |

Valores negativos ou zero são rejeitados.

## Timeout de sessão

Se o usuário iniciar um fluxo (ex: registro de gasto) e ficar mais de
**5 minutos sem responder**, a sessão é resetada automaticamente e o
usuário recebe uma mensagem avisando que a operação foi cancelada.

Isso evita que o bot fique preso aguardando uma resposta que nunca chegará.

## Rate limit

O bot aceita no máximo **3 mensagens por janela de 5 segundos**. Se o
usuário enviar mensagens em rajada, o bot responde listando as mensagens
recebidas e pedindo para reenviar pausadamente.

## Filtragem de mensagens

O webhook filtra automaticamente:

- Mensagens de grupos que não sejam o `WAHA_GROUP_ID` configurado
- Mensagens enviadas pelo próprio bot (detectadas via prefixo invisível `\u200b`)
- Mensagens que não sejam do tipo `message` ou `message.any`
- Payloads acima de 2 MB (proteção contra mídia pesada)

## Fluxo de gerenciamento de gastos (opção 4)

```text
[menu] → 4
  → lista paginada de gastos (5 por página)
  → usuário digita: 2  (escolhe o item)
  → menu de ações: 1-Editar / 2-Excluir / 0-Cancelar
  → [editar] → "Novo valor?" → "Nova categoria?" → "Confirma?" → s → ✅ Atualizado!
  → [excluir] → "Confirma exclusão?" → s → ✅ Excluído!
```

Navegação na lista:

- `p` — página anterior
- `n` — próxima página

## Fluxo de gerenciamento de entradas (opção 5)

Idêntico ao fluxo de gastos, substituindo categoria por fonte.

## Dados registrados

Todos os gastos e entradas criados via WhatsApp ficam vinculados ao usuário
configurado em `WAHA_OWNER_USERNAME`. A descrição do registro indica a origem:

- Gasto: `"Via WhatsApp - <nome da categoria>"`
- Entrada: `"Via WhatsApp - <nome da fonte>"`

Os registros aparecem normalmente no histórico e no dashboard da interface web.
