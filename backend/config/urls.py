from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from financas.serializers import CustomTokenObtainPairSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


urlpatterns = [
    path("admin/", admin.site.urls),
    # Autenticação JWT — obter e renovar tokens.
    path(
        "api/token/", CustomTokenObtainPairView.as_view(), name="token_obtain"
    ),
    path(
        "api/token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),
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
