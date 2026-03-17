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
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer


# CRUD completo para fontes de renda.
class FonteViewSet(ModelViewSet):
    queryset = Fonte.objects.all()
    serializer_class = FonteSerializer


# CRUD completo para gastos.
class GastoViewSet(ModelViewSet):
    queryset = Gasto.objects.all()
    serializer_class = GastoSerializer


# CRUD completo para entradas de dinheiro.
class EntradaViewSet(ModelViewSet):
    queryset = Entrada.objects.all()
    serializer_class = EntradaSerializer
