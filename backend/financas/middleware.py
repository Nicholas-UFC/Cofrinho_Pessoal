import time
from collections.abc import Callable

from django.http import HttpRequest, HttpResponse

_MOBILE_KEYWORDS = ("android", "iphone", "ipad", "mobile")
_ENDPOINTS_IGNORADOS = ("/admin/", "/api/schema/", "/api/docs/")


def _detectar_origem(request: HttpRequest) -> str:
    if "/whatsapp/webhook" in request.path:
        return "whatsapp"
    referer = request.META.get("HTTP_REFERER", "")
    if referer:
        return "web"
    return "api"


def _detectar_dispositivo(user_agent: str) -> str:
    agente = user_agent.lower()
    if any(palavra in agente for palavra in _MOBILE_KEYWORDS):
        return "mobile"
    return "desktop"


def _extrair_ip(request: HttpRequest) -> str | None:
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def _deve_ignorar(path: str) -> bool:
    return any(path.startswith(prefixo) for prefixo in _ENDPOINTS_IGNORADOS)


class MiddlewareLogAcesso:
    def __init__(self, get_response: Callable) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        inicio = time.monotonic()
        response = self.get_response(request)

        if _deve_ignorar(request.path):
            return response

        self._registrar(request, response, inicio)
        return response

    def _registrar(
        self,
        request: HttpRequest,
        response: HttpResponse,
        inicio: float,
    ) -> None:
        from financas.models import LogAcesso  # noqa: PLC0415

        user_agent = request.META.get("HTTP_USER_AGENT", "")
        duracao_ms = int((time.monotonic() - inicio) * 1000)
        usuario = request.user if request.user.is_authenticated else None

        LogAcesso.objects.create(
            usuario=usuario,
            metodo=request.method,
            endpoint=request.path,
            status_code=response.status_code,
            origem=_detectar_origem(request),
            ip=_extrair_ip(request),
            user_agent=user_agent,
            dispositivo=_detectar_dispositivo(user_agent),
            duracao_ms=duracao_ms,
        )
