import json

import pytest
from django.test import Client, override_settings

# ---------------------------------------------------------------------------
# Autenticação do webhook via X-Api-Key — OWASP prática 34
#
# "Use authentication when using external systems that involve sensitive info."
# Verifica que o webhook rejeita requisições sem a chave correta.
# ---------------------------------------------------------------------------

_PAYLOAD_VALIDO = json.dumps({
    "event": "message.any",
    "payload": {
        "body": "menu",
        "fromMe": True,
        "from": "grupo-teste@g.us",
    },
})


@pytest.mark.django_db
@override_settings(WAHA_API_KEY="chave-secreta-teste", WAHA_GROUP_ID="")
def test_webhook_sem_api_key_retorna_403(client: Client) -> None:
    resp = client.post(
        "/api/whatsapp/webhook/",
        data=_PAYLOAD_VALIDO,
        content_type="application/json",
    )
    assert resp.status_code == 403


@pytest.mark.django_db
@override_settings(WAHA_API_KEY="chave-secreta-teste", WAHA_GROUP_ID="")
def test_webhook_com_api_key_errada_retorna_403(client: Client) -> None:
    resp = client.post(
        "/api/whatsapp/webhook/",
        data=_PAYLOAD_VALIDO,
        content_type="application/json",
        HTTP_X_API_KEY="chave-errada",
    )
    assert resp.status_code == 403


@pytest.mark.django_db
@override_settings(WAHA_API_KEY="chave-secreta-teste", WAHA_GROUP_ID="")
def test_webhook_com_api_key_correta_processa(client: Client) -> None:
    resp = client.post(
        "/api/whatsapp/webhook/",
        data=_PAYLOAD_VALIDO,
        content_type="application/json",
        HTTP_X_API_KEY="chave-secreta-teste",
    )
    # Retorna 200 (ignorado ou ok — não 403).
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
