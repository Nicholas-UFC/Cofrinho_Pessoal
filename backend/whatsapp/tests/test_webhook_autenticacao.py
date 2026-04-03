import json

import pytest
from django.test import Client, override_settings

# ---------------------------------------------------------------------------
# Autenticação do webhook
#
# A validação de API key foi removida pois o WAHA envia a chave via header
# WHATSAPP_HOOK_HEADERS configurado no docker-compose, tornando a validação
# no Django redundante para o engine NOWEB.
# O webhook aceita qualquer requisição válida e retorna 200.
# ---------------------------------------------------------------------------

_PAYLOAD_VALIDO = json.dumps(
    {
        "event": "message.any",
        "payload": {
            "body": "menu",
            "fromMe": True,
            "from": "grupo-teste@g.us",
        },
    }
)


@pytest.mark.django_db
@override_settings(WAHA_API_KEY="chave-secreta-teste", WAHA_GROUP_ID="")
def test_webhook_sem_api_key_retorna_200(client: Client) -> None:
    """Sem API key no header, o webhook ainda aceita — validação removida."""
    resp = client.post(
        "/api/whatsapp/webhook/",
        data=_PAYLOAD_VALIDO,
        content_type="application/json",
    )
    assert resp.status_code == 200


@pytest.mark.django_db
@override_settings(WAHA_API_KEY="chave-secreta-teste", WAHA_GROUP_ID="")
def test_webhook_com_api_key_errada_retorna_200(client: Client) -> None:
    """API key errada não rejeita mais — validação foi removida do Django."""
    resp = client.post(
        "/api/whatsapp/webhook/",
        data=_PAYLOAD_VALIDO,
        content_type="application/json",
        HTTP_X_API_KEY="chave-errada",
    )
    assert resp.status_code == 200


@pytest.mark.django_db
@override_settings(WAHA_API_KEY="chave-secreta-teste", WAHA_GROUP_ID="")
def test_webhook_com_api_key_correta_processa(client: Client) -> None:
    resp = client.post(
        "/api/whatsapp/webhook/",
        data=_PAYLOAD_VALIDO,
        content_type="application/json",
        HTTP_X_API_KEY="chave-secreta-teste",
    )
    assert resp.status_code == 200


@pytest.mark.django_db
@override_settings(WAHA_API_KEY="")
def test_webhook_sem_chave_configurada_permite_qualquer(
    client: Client,
) -> None:
    """Quando WAHA_API_KEY não está configurada, não rejeita (modo dev)."""
    resp = client.post(
        "/api/whatsapp/webhook/",
        data=_PAYLOAD_VALIDO,
        content_type="application/json",
    )
    assert resp.status_code == 200
