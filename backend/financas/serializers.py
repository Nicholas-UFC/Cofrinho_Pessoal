from typing import ClassVar

from rest_framework import serializers

from financas.models import Categoria, Entrada, Fonte, Gasto


# Serializer da tabela de categorias de gastos.
class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        # usuario é setado automaticamente pelo servidor via perform_create().
        exclude: ClassVar = ["usuario"]
        read_only_fields: ClassVar = ["id", "criado_em"]

    def validate_nome(self, value: str) -> str:
        # Garante unicidade do nome por usuário a nível de serializer,
        # já que usuario é excluído e o UniqueTogetherValidator não atua.
        user = self.context["request"].user
        qs = Categoria.objects.filter(usuario=user, nome=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "Você já possui uma categoria com este nome."
            )
        return value


# Serializer da tabela de fontes de renda.
class FonteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fonte
        exclude: ClassVar = ["usuario"]
        read_only_fields: ClassVar = ["id", "criado_em"]

    def validate_nome(self, value: str) -> str:
        # Garante unicidade do nome por usuário a nível de serializer.
        user = self.context["request"].user
        qs = Fonte.objects.filter(usuario=user, nome=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "Você já possui uma fonte com este nome."
            )
        return value


# Serializer da tabela de gastos.
class GastoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gasto
        exclude: ClassVar = ["usuario"]
        read_only_fields: ClassVar = ["id", "criado_em"]


# Serializer da tabela de entradas de dinheiro.
class EntradaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entrada
        exclude: ClassVar = ["usuario"]
        read_only_fields: ClassVar = ["id", "criado_em"]
