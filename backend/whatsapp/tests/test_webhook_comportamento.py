import json
from unittest.mock import patch

import httpx
import pytest
from django.test import Client, override_settings

from financas.models import LogAcesso

GRUPO_ID = "120363423218993414@g.us"

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
# Resiliência — erros de envio não derrubam o webhook
# ---------------------------------------------------------------------------
#
# O webhook recebe eventos do WAHA e tenta enviar uma resposta de volta via
# `enviar_mensagem`. Se o servidor WAHA estiver fora do ar ou com timeout, o
# webhook NÃO pode retornar 5xx — isso faria o WAHA reenviar o evento em loop,
# causando respostas duplicadas ao usuário.
#
# A estratégia correta é capturar as exceções de rede e retornar 200 de
# qualquer forma: o evento foi recebido e processado corretamente pelo Django;
# o problema de entrega é externo e não deve ser tratado como falha do webhook.
#
# Os testes de comandos verificam que o texto correto é enviado ao WAHA quando
# o usuário digita um comando válido ou inválido — usando mock no
# `enviar_mensagem` para inspecionar o argumento passado sem precisar de um
# servidor WAHA real.
#
# O teste de auditoria garante que o middleware de LogAcesso registra a chamada
# ao webhook com os metadados corretos, especialmente `origem = "whatsapp"`,
# que é detectado pelo path `/api/whatsapp/webhook/`.
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
    """Timeout de rede ao enviar resposta não deve resultar em 5xx."""
    with patch(
        "whatsapp.views.enviar_mensagem",
        side_effect=httpx.TimeoutException("timeout"),
    ):
        resposta = _post_webhook(client, _PAYLOAD_VALIDO)
    assert resposta.status_code == 200


# ---------------------------------------------------------------------------
# Comandos — resposta correta chega ao WAHA
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@override_settings(WAHA_GROUP_ID=GRUPO_ID)
def test_webhook_comando_desconhecido_responde_lista(
    client: Client,
) -> None:
    """Comando desconhecido deve retornar a lista de comandos disponíveis."""
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
    """Digitar 'menu' deve retornar o menu principal do bot."""
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
    """Toda chamada ao webhook deve ser registrada no LogAcesso com
    a origem identificada como 'whatsapp'."""
    with patch("whatsapp.views.enviar_mensagem"):
        _post_webhook(client, _PAYLOAD_VALIDO)

    log = LogAcesso.objects.filter(endpoint="/api/whatsapp/webhook/").first()
    assert log is not None
    assert log.origem == "whatsapp"
    assert log.metodo == "POST"
