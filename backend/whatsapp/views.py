import json

from django.conf import settings
from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from whatsapp.services import enviar_mensagem, processar_mensagem

_IGNORADO = JsonResponse({"status": "ignorado"})


def _extrair_mensagem(dados: dict, grupo_esperado: str) -> str | None:
    """Retorna o corpo da mensagem se deve ser processada, ou None."""
    if dados.get("event") != "message":
        return None
    payload = dados.get("payload", {})
    if not payload.get("fromMe", False):
        return None
    if payload.get("from", "") != grupo_esperado:
        return None
    return payload.get("body", "").strip() or None


@csrf_exempt
@require_POST
def webhook(request: HttpRequest) -> JsonResponse:
    api_key = request.headers.get("X-Api-Key", "")
    if api_key != getattr(settings, "WAHA_API_KEY", ""):
        return JsonResponse({"erro": "não autorizado"}, status=401)

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
    enviar_mensagem(chat_id, resposta)

    return JsonResponse({"status": "ok"})
