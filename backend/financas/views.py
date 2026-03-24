from typing import ClassVar

from django.db.models import DecimalField, QuerySet, Sum
from django.db.models.functions import Coalesce
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
from rest_framework.viewsets import ModelViewSet

from financas.models import Categoria, Entrada, Fonte, Gasto
from financas.serializers import (
    CategoriaSerializer,
    EntradaSerializer,
    FonteSerializer,
    GastoSerializer,
)


# CRUD completo para categorias de gastos.
# Permissão herdada do DRF global (IsAuthenticated).
class CategoriaViewSet(ModelViewSet):
    serializer_class: type[BaseSerializer] = CategoriaSerializer
    # Desativa paginação — frontend espera lista plana.
    pagination_class = None
    # Filtra apenas categorias do usuário autenticado.
    queryset: ClassVar = Categoria.objects.none()

    def get_queryset(self) -> QuerySet:
        return Categoria.objects.filter(usuario=self.request.user)

    def perform_create(self, serializer: BaseSerializer) -> None:
        # Associa automaticamente o usuário autenticado à categoria.
        serializer.save(usuario=self.request.user)


# CRUD completo para fontes de renda.
class FonteViewSet(ModelViewSet):
    serializer_class: type[BaseSerializer] = FonteSerializer
    # Desativa paginação — frontend espera lista plana.
    pagination_class = None
    queryset: ClassVar = Fonte.objects.none()

    def get_queryset(self) -> QuerySet:
        return Fonte.objects.filter(usuario=self.request.user)

    def perform_create(self, serializer: BaseSerializer) -> None:
        serializer.save(usuario=self.request.user)


# CRUD completo para gastos.
# Filtros: categoria, data, data__gte, data__lte, valor__gte, valor__lte.
class GastoViewSet(ModelViewSet):
    serializer_class: type[BaseSerializer] = GastoSerializer
    queryset: ClassVar = Gasto.objects.none()
    filterset_fields: ClassVar = {
        "categoria": ["exact"],
        "data": ["exact", "gte", "lte"],
        "valor": ["gte", "lte"],
    }

    def get_queryset(self) -> QuerySet:
        return Gasto.objects.filter(usuario=self.request.user)

    def perform_create(self, serializer: BaseSerializer) -> None:
        serializer.save(usuario=self.request.user)


# CRUD completo para entradas de dinheiro.
# Filtros: fonte, data, data__gte, data__lte, valor__gte, valor__lte.
class EntradaViewSet(ModelViewSet):
    serializer_class: type[BaseSerializer] = EntradaSerializer
    queryset: ClassVar = Entrada.objects.none()
    filterset_fields: ClassVar = {
        "fonte": ["exact"],
        "data": ["exact", "gte", "lte"],
        "valor": ["gte", "lte"],
    }

    def get_queryset(self) -> QuerySet:
        return Entrada.objects.filter(usuario=self.request.user)

    def perform_create(self, serializer: BaseSerializer) -> None:
        serializer.save(usuario=self.request.user)


# Resumo financeiro — saldo, totais e gastos por categoria.
# Rota manual: GET /api/financas/resumo/
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def resumo(request: Request) -> Response:
    usuario = request.user

    # Coalesce garante 0 quando não há registros, em vez de None.
    soma_ou_zero = Coalesce(
        Sum("valor"),
        0,
        output_field=DecimalField(max_digits=10, decimal_places=2),
    )

    total_entradas = Entrada.objects.filter(usuario=usuario).aggregate(
        total=soma_ou_zero
    )["total"]
    total_gastos = Gasto.objects.filter(usuario=usuario).aggregate(
        total=soma_ou_zero
    )["total"]

    # Agrupa gastos do usuário por nome da categoria e soma os valores.
    gastos_por_categoria = list(
        Gasto.objects.filter(usuario=usuario)
        .values("categoria__nome")
        .annotate(total=soma_ou_zero)
        .order_by("categoria__nome")
    )

    return Response(
        {
            "total_entradas": total_entradas,
            "total_gastos": total_gastos,
            "saldo": total_entradas - total_gastos,
            "gastos_por_categoria": gastos_por_categoria,
        }
    )
