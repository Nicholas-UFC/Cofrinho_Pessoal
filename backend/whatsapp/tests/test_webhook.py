import json
from unittest.mock import patch

import httpx
import pytest
from django.test import Client, override_settings

from financas.models import LogAcesso
from whatsapp.services import PREFIXO_BOT

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


# ---------------------------------------------------------------------------
# Erro de envio de mensagem
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@override_settings(WAHA_GROUP_ID=GRUPO_ID)
def test_webhook_retorna_200_mesmo_com_falha_no_envio(
    client: Client,
) -> None:
    """Falha no envio ao WAHA não deve derrubar o webhook."""
    with patch(
        "whatsapp.views.enviar_mensagem",
        side_effect=httpx.ConnectError("WAHA fora do ar"),
    ):
        resposta = _post_webhook(client, _PAYLOAD_VALIDO)
    assert resposta.status_code == 200


@pytest.mark.django_db
@override_settings(WAHA_GROUP_ID=GRUPO_ID)
def test_webhook_retorna_200_com_timeout_no_envio(client: Client) -> None:
    with patch(
        "whatsapp.views.enviar_mensagem",
        side_effect=httpx.TimeoutException("timeout"),
    ):
        resposta = _post_webhook(client, _PAYLOAD_VALIDO)
    assert resposta.status_code == 200


# ---------------------------------------------------------------------------
# Comando desconhecido chega pelo webhook
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@override_settings(WAHA_GROUP_ID=GRUPO_ID)
def test_webhook_comando_desconhecido_responde_lista(
    client: Client,
) -> None:
    dados = {
        **_PAYLOAD_VALIDO,
        "payload": {**_PAYLOAD_VALIDO["payload"], "body": "oi"},
    }
    with patch("whatsapp.views.enviar_mensagem") as mock_enviar:
        resposta = _post_webhook(client, dados)
    assert resposta.status_code == 200
    texto_enviado = mock_enviar.call_args[0][1]
    assert "Não conheço o comando" in texto_enviado
    assert "Comandos disponíveis" in texto_enviado


@pytest.mark.django_db
@override_settings(WAHA_GROUP_ID=GRUPO_ID)
def test_webhook_digitar_menu_exibe_menu(client: Client) -> None:
    dados = {
        **_PAYLOAD_VALIDO,
        "payload": {**_PAYLOAD_VALIDO["payload"], "body": "menu"},
    }
    with patch("whatsapp.views.enviar_mensagem") as mock_enviar:
        resposta = _post_webhook(client, dados)
    assert resposta.status_code == 200
    texto_enviado = mock_enviar.call_args[0][1]
    assert "Cofrinho Pessoal" in texto_enviado


# ---------------------------------------------------------------------------
# Auditoria via middleware
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@override_settings(WAHA_GROUP_ID=GRUPO_ID)
def test_webhook_gera_log_acesso(client: Client) -> None:
    with patch("whatsapp.views.enviar_mensagem"):
        _post_webhook(client, _PAYLOAD_VALIDO)

    log = LogAcesso.objects.filter(
        endpoint="/api/whatsapp/webhook/"
    ).first()
    assert log is not None
    assert log.origem == "whatsapp"
    assert log.metodo == "POST"
