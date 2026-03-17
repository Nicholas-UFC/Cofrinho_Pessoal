from typing import ClassVar

from rest_framework import serializers

from financas.models import Categoria, Entrada, Fonte, Gasto


# Serializer da tabela de categorias de gastos.
class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = "__all__"
        # criado_em é auto_now_add — nunca deve ser enviado pelo cliente.
        read_only_fields: ClassVar = ["criado_em"]


# Serializer da tabela de fontes de renda.
class FonteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fonte
        fields = "__all__"
        read_only_fields: ClassVar = ["criado_em"]


# Serializer da tabela de gastos.
class GastoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gasto
        fields = "__all__"
        read_only_fields: ClassVar = ["criado_em"]


# Serializer da tabela de entradas de dinheiro.
class EntradaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entrada
        fields = "__all__"
        read_only_fields: ClassVar = ["criado_em"]
