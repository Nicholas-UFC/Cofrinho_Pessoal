import time
from collections.abc import Callable

from django.http import HttpRequest, HttpResponse

_MOBILE_KEYWORDS = ("android", "iphone", "ipad", "mobile")
_ENDPOINTS_IGNORADOS = ("/admin/", "/api/schema/", "/api/docs/")

# Limites de tamanho para campos de log — OWASP prática 116.
_MAX_USER_AGENT = 500
_MAX_ENDPOINT = 255


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


def _sanitizar_ascii(texto: str, limite: int) -> str:
    """Remove não-ASCII e bytes de controle; trunca — OWASP 9, 116."""
    sanitizado = texto.encode("ascii", errors="ignore").decode("ascii")
    # PostgreSQL rejeita NUL (0x00); remove caracteres de controle.
    sanitizado = sanitizado.translate(
        str.maketrans("", "", "".join(chr(i) for i in range(32)))
    )
    return sanitizado[:limite]


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

        user_agent_raw = request.META.get("HTTP_USER_AGENT", "")
        user_agent = _sanitizar_ascii(user_agent_raw, _MAX_USER_AGENT)
        endpoint = _sanitizar_ascii(request.path, _MAX_ENDPOINT)
        duracao_ms = int((time.monotonic() - inicio) * 1000)
        usuario = request.user if request.user.is_authenticated else None

        LogAcesso.objects.create(
            usuario=usuario,
            metodo=request.method,
            endpoint=endpoint,
            status_code=response.status_code,
            origem=_detectar_origem(request),
            ip=_extrair_ip(request),
            user_agent=user_agent,
            dispositivo=_detectar_dispositivo(user_agent),
            duracao_ms=duracao_ms,
        )


# Cabeçalhos de segurança — OWASP práticas 140, 150, 162.
_CSP = (
    "default-src 'self'; "
    "script-src 'self'; "
    "style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data:; "
    "font-src 'self'; "
    "connect-src 'self'; "
    "frame-ancestors 'none';"
)


class MiddlewareSecurityHeaders:
    def __init__(self, get_response: Callable) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)
        self._adicionar_headers(request, response)
        return response

    def _adicionar_headers(
        self, request: HttpRequest, response: HttpResponse
    ) -> None:
        # Remove informações do servidor — prática 162.
        response.headers.pop("Server", None)
        response.headers.pop("X-Powered-By", None)

        # Política de conteúdo — previne XSS e injeção.
        response["Content-Security-Policy"] = _CSP

        # Política de referer — prática 150.
        response["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Restringe acesso a APIs do navegador — prática 162.
        response["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=()"
        )

        # Impede cache de dados sensíveis — prática 140.
        if request.path.startswith("/api/"):
            response["Cache-Control"] = "no-store"
            response["Pragma"] = "no-cache"
