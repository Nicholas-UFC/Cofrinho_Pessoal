import json
from unittest.mock import patch

import pytest
from django.test import Client, override_settings

from whatsapp.services import PREFIXO_BOT

# ---------------------------------------------------------------------------
# Webhook — filtragem de eventos e mensagens do WAHA
# ---------------------------------------------------------------------------
#
# O webhook recebe todos os eventos do WAHA (mensagens enviadas e recebidas,
# mudanças de status de sessão, etc.) e precisa decidir o que processar.
# Esta suíte verifica os três níveis de filtragem implementados na view:
#
# 1. FORMATO DO PAYLOAD: payloads inválidos (JSON malformado) retornam 400.
#    Payloads grandes demais (>2 MB — típico de áudio/mídia) são rejeitados
#    silenciosamente com 200, sem tentar ler o body, para evitar que o Django
#    lance RequestDataTooBig antes de chegarmos ao try/except da view.
#
# 2. FILTROS DE ORIGEM: apenas mensagens do grupo configurado em WAHA_GROUP_ID
#    são processadas. IDs de grupos diferentes, IDs parecidos (mas com um
#    dígito diferente), chats individuais e ausência de configuração devem
#    resultar em 200 sem chamar `enviar_mensagem`.
#
# 3. FILTROS DE CONTEÚDO E REMETENTE: apenas mensagens com fromMe=True são
#    aceitas (o bot lê mensagens enviadas pelo número do bot). Mensagens com
#    fromMe=False (enviadas por outros membros do grupo) são ignoradas.
#    Mensagens cujo body começa com PREFIXO_BOT são ecos das próprias
#    respostas do bot e devem ser descartadas para evitar loop infinito.
#    Eventos que não sejam "message" ou "message.any" também são ignorados.
#
# Testes de comportamento (erros de envio, comandos e auditoria) estão em
# `test_webhook_comportamento.py`.
# ---------------------------------------------------------------------------

GRUPO_ID = "120363423218993414@g.us"
CHAT_INDIVIDUAL = "5588999999999@s.whatsapp.net"
GRUPO_PARECIDO = "120363423218993415@g.us"
OUTRO_GRUPO = "558897295869-1613420541@g.us"

_PAYLOAD_VALIDO: dict = {
    "event": "message",
    "session": "default",
    "payload": {
        "id": "msg_001",
        "from": GRUPO_ID,
        "fromMe": True,
        "body": "3",
    },
}


def _post_webhook(client: Client, dados: dict) -> ...:
    return client.post(
        "/api/whatsapp/webhook/",
        data=json.dumps(dados),
        content_type="application/json",
    )


# ---------------------------------------------------------------------------
# Formato do payload
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@override_settings(WAHA_GROUP_ID=GRUPO_ID)
def test_webhook_retorna_200(client: Client) -> None:
    with patch("whatsapp.views.enviar_mensagem"):
        resposta = _post_webhook(client, _PAYLOAD_VALIDO)
    assert resposta.status_code == 200


@pytest.mark.django_db
@override_settings(WAHA_GROUP_ID=GRUPO_ID)
def test_webhook_payload_invalido_retorna_400(client: Client) -> None:
    resposta = client.post(
        "/api/whatsapp/webhook/",
        data="nao_e_json",
        content_type="application/json",
    )
    assert resposta.status_code == 400


@pytest.mark.django_db
@override_settings(WAHA_GROUP_ID=GRUPO_ID)
def test_webhook_payload_grande_retorna_200_ignorado(client: Client) -> None:
    """Mídia/áudio com payload enorme não deve derrubar o webhook."""
    resposta = client.post(
        "/api/whatsapp/webhook/",
        data="{}",
        content_type="application/json",
        CONTENT_LENGTH=str(3 * 1024 * 1024),  # 3 MB > limite de 2 MB
    )
    assert resposta.status_code == 200


# ---------------------------------------------------------------------------
# Filtros de mensagem — origem
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@override_settings(WAHA_GROUP_ID=GRUPO_ID)
def test_webhook_ignora_grupo_errado(client: Client) -> None:
    dados = {
        **_PAYLOAD_VALIDO,
        "payload": {**_PAYLOAD_VALIDO["payload"], "from": OUTRO_GRUPO},
    }
    with patch("whatsapp.views.enviar_mensagem") as mock_enviar:
        resposta = _post_webhook(client, dados)
    assert resposta.status_code == 200
    mock_enviar.assert_not_called()


@pytest.mark.django_db
@override_settings(WAHA_GROUP_ID=GRUPO_ID)
def test_webhook_ignora_grupo_com_id_parecido(client: Client) -> None:
    """ID quase idêntico mas diferente de um dígito deve ser rejeitado."""
    dados = {
        **_PAYLOAD_VALIDO,
        "payload": {**_PAYLOAD_VALIDO["payload"], "from": GRUPO_PARECIDO},
    }
    with patch("whatsapp.views.enviar_mensagem") as mock_enviar:
        resposta = _post_webhook(client, dados)
    assert resposta.status_code == 200
    mock_enviar.assert_not_called()


@pytest.mark.django_db
@override_settings(WAHA_GROUP_ID=GRUPO_ID)
def test_webhook_ignora_chat_individual(client: Client) -> None:
    """Mensagem de conversa privada (não grupo) deve ser ignorada."""
    dados = {
        **_PAYLOAD_VALIDO,
        "payload": {**_PAYLOAD_VALIDO["payload"], "from": CHAT_INDIVIDUAL},
    }
    with patch("whatsapp.views.enviar_mensagem") as mock_enviar:
        resposta = _post_webhook(client, dados)
    assert resposta.status_code == 200
    mock_enviar.assert_not_called()


@pytest.mark.django_db
@override_settings(WAHA_GROUP_ID="")
def test_webhook_ignora_tudo_quando_group_id_nao_configurado(
    client: Client,
) -> None:
    """Sem WAHA_GROUP_ID configurado, nenhuma mensagem é processada."""
    with patch("whatsapp.views.enviar_mensagem") as mock_enviar:
        resposta = _post_webhook(client, _PAYLOAD_VALIDO)
    assert resposta.status_code == 200
    mock_enviar.assert_not_called()


# ---------------------------------------------------------------------------
# Filtros de mensagem — conteúdo e remetente
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@override_settings(WAHA_GROUP_ID=GRUPO_ID)
def test_webhook_ignora_from_me_false(client: Client) -> None:
    dados = {
        **_PAYLOAD_VALIDO,
        "payload": {**_PAYLOAD_VALIDO["payload"], "fromMe": False},
    }
    with patch("whatsapp.views.enviar_mensagem") as mock_enviar:
        resposta = _post_webhook(client, dados)
    assert resposta.status_code == 200
    mock_enviar.assert_not_called()


@pytest.mark.django_db
@override_settings(WAHA_GROUP_ID=GRUPO_ID)
def test_webhook_ignora_echo_do_bot(client: Client) -> None:
    """Resposta enviada pelo próprio bot não deve ser reprocessada."""
    dados = {
        **_PAYLOAD_VALIDO,
        "payload": {
            **_PAYLOAD_VALIDO["payload"],
            "body": PREFIXO_BOT + "🤖 *Cofrinho Pessoal*",
        },
    }
    with patch("whatsapp.views.enviar_mensagem") as mock_enviar:
        resposta = _post_webhook(client, dados)
    assert resposta.status_code == 200
    mock_enviar.assert_not_called()


@pytest.mark.django_db
@override_settings(WAHA_GROUP_ID=GRUPO_ID)
def test_webhook_ignora_evento_nao_message(client: Client) -> None:
    dados = {**_PAYLOAD_VALIDO, "event": "session.status"}
    with patch("whatsapp.views.enviar_mensagem") as mock_enviar:
        resposta = _post_webhook(client, dados)
    assert resposta.status_code == 200
    mock_enviar.assert_not_called()


@pytest.mark.django_db
@override_settings(WAHA_GROUP_ID=GRUPO_ID)
def test_webhook_aceita_evento_message_any(client: Client) -> None:
    dados = {**_PAYLOAD_VALIDO, "event": "message.any"}
    with patch("whatsapp.views.enviar_mensagem") as mock_enviar:
        resposta = _post_webhook(client, dados)
    assert resposta.status_code == 200
    mock_enviar.assert_called_once()

