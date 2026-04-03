import json

import pytest
from django.test import Client, override_settings

# ---------------------------------------------------------------------------
# Autenticação do webhook via WAHA_WEBHOOK_SECRET
#
# Quando WAHA_WEBHOOK_SECRET está configurado, o Django exige o header
# X-Webhook-Secret com o valor correto antes de processar qualquer payload.
# Quando vazio (modo dev), aceita todas as requisições.
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
@override_settings(WAHA_WEBHOOK_SECRET="token-secreto", WAHA_GROUP_ID="")
def test_webhook_sem_token_retorna_403(client: Client) -> None:
    """Sem o header X-Webhook-Secret, o webhook rejeita com 403."""
    resp = client.post(
        "/api/whatsapp/webhook/",
        data=_PAYLOAD_VALIDO,
        content_type="application/json",
    )
    assert resp.status_code == 403


@pytest.mark.django_db
@override_settings(WAHA_WEBHOOK_SECRET="token-secreto", WAHA_GROUP_ID="")
def test_webhook_com_token_errado_retorna_403(client: Client) -> None:
    """Token errado no header também deve ser rejeitado com 403."""
    resp = client.post(
        "/api/whatsapp/webhook/",
        data=_PAYLOAD_VALIDO,
        content_type="application/json",
        HTTP_X_WEBHOOK_SECRET="token-errado",
    )
    assert resp.status_code == 403


@pytest.mark.django_db
@override_settings(WAHA_WEBHOOK_SECRET="token-secreto", WAHA_GROUP_ID="")
def test_webhook_com_token_correto_processa(client: Client) -> None:
    """Token correto no header deve permitir o processamento."""
    resp = client.post(
        "/api/whatsapp/webhook/",
        data=_PAYLOAD_VALIDO,
        content_type="application/json",
        HTTP_X_WEBHOOK_SECRET="token-secreto",
    )
    assert resp.status_code == 200


@pytest.mark.django_db
@override_settings(WAHA_WEBHOOK_SECRET="", WAHA_GROUP_ID="")
def test_webhook_sem_segredo_configurado_aceita_tudo(client: Client) -> None:
    """WAHA_WEBHOOK_SECRET vazio = modo dev; aceita sem header."""
    resp = client.post(
        "/api/whatsapp/webhook/",
        data=_PAYLOAD_VALIDO,
        content_type="application/json",
    )
    assert resp.status_code == 200
