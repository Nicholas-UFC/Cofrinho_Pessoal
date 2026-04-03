import contextlib
import json

from django.conf import settings
from django.contrib import admin
from django.http import HttpRequest, JsonResponse
from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from financas.autenticacao import CookieJWTAuthentication
from financas.serializers import CustomTokenObtainPairSerializer


def _cookie_seguro() -> bool:
    return not settings.DEBUG


def _definir_cookies_token(
    response: JsonResponse, access: str, refresh: str
) -> None:
    """Define cookies httpOnly para access e refresh — OWASP prática 76."""
    seguro = _cookie_seguro()
    response.set_cookie(
        "access",
        access,
        httponly=True,
        secure=seguro,
        samesite="Lax",
        max_age=3600,
    )
    response.set_cookie(
        "refresh",
        refresh,
        httponly=True,
        secure=seguro,
        samesite="Lax",
        max_age=7 * 24 * 3600,
    )


class CookieTokenObtainPairView(TokenObtainPairView):
    """Login via cookie httpOnly — OWASP prática 76."""

    serializer_class = CustomTokenObtainPairSerializer

    def post(  # type: ignore[override]
        self,
        request: Request,
        *args: object,
        **kwargs: object,
    ) -> JsonResponse | Response:
        resposta_original = super().post(request, *args, **kwargs)
        if resposta_original.status_code != status.HTTP_200_OK:
            return resposta_original

        access = resposta_original.data.get("access", "")
        refresh = resposta_original.data.get("refresh", "")
        payload = AccessToken(access)
        response = JsonResponse(
            {
                "username": payload.get("username"),
                "is_staff": payload.get("is_staff", False),
            }
        )
        _definir_cookies_token(response, access, refresh)
        return response


# Handlers genéricos de erro — OWASP práticas 107-109.
def handler404(  # type: ignore[misc]
    request: HttpRequest,  # noqa: ARG001
    exception: Exception,  # noqa: ARG001
) -> JsonResponse:
    return JsonResponse({"erro": "Recurso não encontrado."}, status=404)


def handler500(  # type: ignore[misc]
    request: HttpRequest,  # noqa: ARG001
) -> JsonResponse:
    return JsonResponse({"erro": "Erro interno do servidor."}, status=500)


def _autenticar_jwt(request: HttpRequest) -> bool:
    for cls in (CookieJWTAuthentication, JWTAuthentication):
        try:
            resultado = cls().authenticate(request)  # type: ignore[arg-type]
            if resultado is not None:
                return True
        except Exception:
            continue
    return False


def _extrair_refresh(request: HttpRequest) -> str | None:
    # Cookie tem prioridade sobre body.
    refresh = request.COOKIES.get("refresh")
    if refresh:
        return refresh
    if request.content_type == "application/json":
        try:
            return json.loads(request.body).get("refresh")
        except (json.JSONDecodeError, ValueError):
            return None
    return request.POST.get("refresh")


@csrf_exempt
@require_POST
def renovar_token_cookie(request: HttpRequest) -> JsonResponse:
    """Renova o access token via cookie httpOnly — OWASP prática 76."""
    refresh = request.COOKIES.get("refresh")
    if not refresh:
        return JsonResponse({"erro": "Token de refresh ausente."}, status=401)

    serializer = TokenRefreshSerializer(data={"refresh": refresh})
    try:
        serializer.is_valid(raise_exception=True)
    except Exception:
        return JsonResponse(
            {"erro": "Token inválido ou expirado."}, status=401
        )

    novo_access = str(serializer.validated_data["access"])
    novo_refresh = str(serializer.validated_data.get("refresh", refresh))

    response = JsonResponse({"status": "ok"})
    _definir_cookies_token(response, novo_access, novo_refresh)
    return response


@csrf_exempt
@require_POST
def logout(request: HttpRequest) -> JsonResponse:
    """Blacklista o refresh token e limpa cookies — OWASP prática 62."""
    if not _autenticar_jwt(request):
        return JsonResponse({"erro": "Autenticação necessária."}, status=401)

    refresh_token = _extrair_refresh(request)
    if not refresh_token:
        return JsonResponse(
            {"erro": "Token de refresh necessário."}, status=400
        )

    # Token já inválido — ainda limpa os cookies.
    with contextlib.suppress(InvalidToken, TokenError):
        RefreshToken(refresh_token).blacklist()

    response = JsonResponse({"status": "logout realizado com sucesso."})
    response.delete_cookie("access")
    response.delete_cookie("refresh")
    return response


@api_view(["GET"])
def me(request: HttpRequest) -> Response:
    """Retorna informações do usuário autenticado."""
    return Response(
        {
            "username": request.user.username,  # type: ignore[union-attr]
            "is_staff": request.user.is_staff,  # type: ignore[union-attr]
        }
    )


urlpatterns = [
    path("admin/", admin.site.urls),
    # Autenticação JWT via cookie httpOnly — OWASP prática 76.
    path(
        "api/token/",
        CookieTokenObtainPairView.as_view(),
        name="token_obtain",
    ),
    path("api/token/refresh/", renovar_token_cookie, name="token_refresh"),
    path("api/token/logout/", logout, name="token_logout"),
    path("api/me/", me, name="me"),
    # Documentação automática da API (OpenAPI + Swagger UI).
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    # URLs do app financas — definidas em financas/urls.py.
    path("api/financas/", include("financas.urls")),
    # URLs do app whatsapp — webhook do WAHA.
    path("api/whatsapp/", include("whatsapp.urls")),
]
