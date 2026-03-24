from typing import ClassVar

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from financas.models import Categoria, Entrada, Fonte, Gasto


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):  # type: ignore[override]
        token = super().get_token(user)
        token["username"] = user.username
        token["is_staff"] = user.is_staff
        return token


# Serializer da tabela de categorias de gastos.
class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        # usuario é setado automaticamente pelo servidor via perform_create().
        exclude: ClassVar = ["usuario"]
        read_only_fields: ClassVar = ["id", "criado_em"]

    def validate_nome(self, valor: str) -> str:
        # Garante unicidade do nome por usuário a nível de serializer,
        # já que usuario é excluído e o UniqueTogetherValidator não atua.
        usuario = self.context["request"].user
        registros = Categoria.objects.filter(usuario=usuario, nome=valor)
        if self.instance:
            registros = registros.exclude(pk=self.instance.pk)
        if registros.exists():
            raise serializers.ValidationError(
                "Você já possui uma categoria com este nome."
            )
        return valor


# Serializer da tabela de fontes de renda.
class FonteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fonte
        exclude: ClassVar = ["usuario"]
        read_only_fields: ClassVar = ["id", "criado_em"]

    def validate_nome(self, valor: str) -> str:
        # Garante unicidade do nome por usuário a nível de serializer.
        usuario = self.context["request"].user
        registros = Fonte.objects.filter(usuario=usuario, nome=valor)
        if self.instance:
            registros = registros.exclude(pk=self.instance.pk)
        if registros.exists():
            raise serializers.ValidationError(
                "Você já possui uma fonte com este nome."
            )
        return valor


# Serializer da tabela de gastos.
class GastoSerializer(serializers.ModelSerializer):
    categoria_nome = serializers.CharField(source="categoria.nome", read_only=True)

    class Meta:
        model = Gasto
        exclude: ClassVar = ["usuario"]
        read_only_fields: ClassVar = ["id", "criado_em", "categoria_nome"]


# Serializer da tabela de entradas de dinheiro.
class EntradaSerializer(serializers.ModelSerializer):
    fonte_nome = serializers.CharField(source="fonte.nome", read_only=True)

    class Meta:
        model = Entrada
        exclude: ClassVar = ["usuario"]
        read_only_fields: ClassVar = ["id", "criado_em", "fonte_nome"]
