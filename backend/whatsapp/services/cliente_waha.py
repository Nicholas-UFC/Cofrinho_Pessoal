import logging

import httpx
from django.conf import settings

logger = logging.getLogger(__name__)

# IDs das mensagens enviadas pelo bot — usados para ignorar o echo do
# message.any
_ids_enviados: set[str] = set()
_MAX_IDS_ENVIADOS = 200


def ids_enviados_pelo_bot() -> set[str]:
    return _ids_enviados


def _registrar_id_enviado(resposta: httpx.Response) -> None:
    try:
        msg_id = resposta.json().get("id")
    except Exception:
        return
    if not msg_id:
        return
    _ids_enviados.add(msg_id)
    if len(_ids_enviados) > _MAX_IDS_ENVIADOS:
        _ids_enviados.discard(next(iter(_ids_enviados)))


def enviar_mensagem(chat_id: str, texto: str) -> None:
    url = f"{settings.WAHA_API_URL}/api/sendText"
    headers = {"X-Api-Key": settings.WAHA_API_KEY}
    payload = {
        "chatId": chat_id,
        "text": texto,
        "session": getattr(settings, "WAHA_SESSION", "default"),
    }
    try:
        resposta = httpx.post(
            url, json=payload, headers=headers, timeout=10
        )
        _registrar_id_enviado(resposta)
    except httpx.ConnectError as exc:
        logger.error(
            "Falha de conexão ao WAHA (%s): %s",
            url,
            exc,
        )
        raise
    except httpx.TimeoutException as exc:
        logger.warning("Timeout ao enviar mensagem para %s: %s", chat_id, exc)
        raise
