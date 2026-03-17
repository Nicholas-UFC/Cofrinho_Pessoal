from django.urls import path
from rest_framework.routers import DefaultRouter

from financas.views import (
    CategoriaViewSet,
    EntradaViewSet,
    FonteViewSet,
    GastoViewSet,
    resumo,
)

# Router local do app financas — cada ViewSet gera automaticamente
# os endpoints: GET /list, POST /list, GET /{id}, PUT /{id},
# PATCH /{id}, DELETE /{id}.
router = DefaultRouter()
router.register("categorias", CategoriaViewSet, basename="categoria")
router.register("fontes", FonteViewSet, basename="fonte")
router.register("gastos", GastoViewSet, basename="gasto")
router.register("entradas", EntradaViewSet, basename="entrada")

# Rota manual para o endpoint de resumo financeiro.
urlpatterns = [*router.urls, path("resumo/", resumo, name="resumo")]
