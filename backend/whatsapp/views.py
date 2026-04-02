import json
import logging

import httpx
from django.conf import settings
from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from whatsapp.services import PREFIXO_BOT, enviar_mensagem, processar_mensagem

logger = logging.getLogger(__name__)

_IGNORADO = JsonResponse({"status": "ignorado"})
# 2 MB — suficiente para texto, bloqueia payloads de mídia
_MAX_BODY_BYTES = 2 * 1024 * 1024


def _extrair_mensagem(dados: dict, grupo_esperado: str) -> str | None:
    """Retorna o corpo da mensagem se deve ser processada, ou None."""
    if dados.get("event") not in ("message", "message.any"):
        return None
    payload = dados.get("payload", {})
    corpo = payload.get("body", "") or ""
    if corpo.startswith(PREFIXO_BOT):
        return None
    if payload.get("from", "") != grupo_esperado:
        return None
    return corpo.strip() or None


@csrf_exempt
@require_POST
def webhook(request: HttpRequest) -> JsonResponse:
    tamanho = int(request.META.get("CONTENT_LENGTH") or 0)
    if tamanho > _MAX_BODY_BYTES:
        return _IGNORADO

    try:
        dados = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"erro": "payload inválido"}, status=400)

    grupo_esperado = getattr(settings, "WAHA_GROUP_ID", "")
    corpo = _extrair_mensagem(dados, grupo_esperado)
    if corpo is None:
        return _IGNORADO

    chat_id = dados["payload"]["from"]
    resposta = processar_mensagem(chat_id, corpo)

    try:
        enviar_mensagem(chat_id, resposta)
    except httpx.HTTPError as exc:
        logger.warning("Falha ao enviar mensagem para %s: %s", chat_id, exc)

    return JsonResponse({"status": "ok"})
