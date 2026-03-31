import json

from django.contrib import admin
from django.http import HttpRequest, JsonResponse
from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from financas.serializers import CustomTokenObtainPairSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# Handlers genéricos de erro — OWASP práticas 107-109.
def handler404(  # type: ignore[misc]
    request: HttpRequest, exception: Exception  # noqa: ARG001
) -> JsonResponse:
    return JsonResponse({"erro": "Recurso não encontrado."}, status=404)


def handler500(  # type: ignore[misc]
    request: HttpRequest,  # noqa: ARG001
) -> JsonResponse:
    return JsonResponse({"erro": "Erro interno do servidor."}, status=500)


def _autenticar_jwt(request: HttpRequest) -> bool:
    auth = JWTAuthentication()
    try:
        resultado = auth.authenticate(request)  # type: ignore[arg-type]
        return resultado is not None
    except Exception:
        return False


def _extrair_refresh(request: HttpRequest) -> str | None:
    if request.content_type == "application/json":
        try:
            return json.loads(request.body).get("refresh")
        except (json.JSONDecodeError, ValueError):
            return None
    return request.POST.get("refresh")


@csrf_exempt
@require_POST
def logout(request: HttpRequest) -> JsonResponse:
    """Blacklista o refresh token — OWASP prática 62."""
    if not _autenticar_jwt(request):
        return JsonResponse(
            {"erro": "Autenticação necessária."}, status=401
        )

    refresh_token = _extrair_refresh(request)
    if not refresh_token:
        return JsonResponse(
            {"erro": "Token de refresh necessário."}, status=400
        )

    try:
        RefreshToken(refresh_token).blacklist()
    except (InvalidToken, TokenError):
        return JsonResponse(
            {"erro": "Token inválido ou já expirado."}, status=400
        )

    return JsonResponse({"status": "logout realizado com sucesso."})


urlpatterns = [
    path("admin/", admin.site.urls),
    # Autenticação JWT — obter, renovar e invalidar tokens.
    path(
        "api/token/", CustomTokenObtainPairView.as_view(), name="token_obtain"
    ),
    path(
        "api/token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path("api/token/logout/", logout, name="token_logout"),
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
