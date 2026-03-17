from typing import ClassVar

from django.db.models import DecimalField, Sum
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
    queryset: ClassVar = Categoria.objects.all()
    serializer_class: type[BaseSerializer] = CategoriaSerializer


# CRUD completo para fontes de renda.
class FonteViewSet(ModelViewSet):
    queryset: ClassVar = Fonte.objects.all()
    serializer_class: type[BaseSerializer] = FonteSerializer


# CRUD completo para gastos.
# Filtros: categoria, data, data__gte, data__lte, valor__gte, valor__lte.
class GastoViewSet(ModelViewSet):
    queryset: ClassVar = Gasto.objects.all()
    serializer_class: type[BaseSerializer] = GastoSerializer
    filterset_fields: ClassVar = {
        "categoria": ["exact"],
        "data": ["exact", "gte", "lte"],
        "valor": ["gte", "lte"],
    }


# CRUD completo para entradas de dinheiro.
# Filtros: fonte, data, data__gte, data__lte, valor__gte, valor__lte.
class EntradaViewSet(ModelViewSet):
    queryset: ClassVar = Entrada.objects.all()
    serializer_class: type[BaseSerializer] = EntradaSerializer
    filterset_fields: ClassVar = {
        "fonte": ["exact"],
        "data": ["exact", "gte", "lte"],
        "valor": ["gte", "lte"],
    }


# Resumo financeiro — saldo, totais e gastos por categoria.
# Rota manual: GET /api/financas/resumo/
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def resumo(request: Request) -> Response:  # noqa: ARG001
    # Coalesce garante 0 quando não há registros, em vez de None.
    zero = Coalesce(
        Sum("valor"),
        0,
        output_field=DecimalField(max_digits=10, decimal_places=2),
    )

    total_entradas = Entrada.objects.aggregate(total=zero)["total"]
    total_gastos = Gasto.objects.aggregate(total=zero)["total"]

    # Agrupa gastos por nome da categoria e soma os valores.
    gastos_por_categoria = list(
        Gasto.objects.values("categoria__nome")
        .annotate(total=zero)
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
