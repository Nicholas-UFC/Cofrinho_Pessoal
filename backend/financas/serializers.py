from typing import ClassVar

from rest_framework import serializers
from rest_framework_simplejwt.models import TokenUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import Token

from financas.models import Categoria, Entrada, Fonte, Gasto
from financas.services.entrada import criar_entrada
from financas.services.gasto import criar_gasto
from financas.validators import validar_caracteres_seguros


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user: TokenUser) -> Token:
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
        validar_caracteres_seguros(valor)
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
        validar_caracteres_seguros(valor)
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
    categoria_nome = serializers.CharField(
        source="categoria.nome", read_only=True
    )

    class Meta:
        model = Gasto
        exclude: ClassVar = ["usuario"]
        read_only_fields: ClassVar = ["id", "criado_em", "categoria_nome"]

    def validate_descricao(self, valor: str) -> str:
        validar_caracteres_seguros(valor)
        return valor

    def create(self, validated_data: dict) -> Gasto:
        # usuario é injetado via perform_create(serializer.save(usuario=...)).
        usuario = validated_data.pop("usuario")
        return criar_gasto(
            usuario=usuario,
            valor=validated_data["valor"],
            categoria=validated_data["categoria"],
            descricao=validated_data["descricao"],
            data=validated_data["data"],
        )


# Serializer da tabela de entradas de dinheiro.
class EntradaSerializer(serializers.ModelSerializer):
    fonte_nome = serializers.CharField(source="fonte.nome", read_only=True)

    class Meta:
        model = Entrada
        exclude: ClassVar = ["usuario"]
        read_only_fields: ClassVar = ["id", "criado_em", "fonte_nome"]

    def validate_descricao(self, valor: str) -> str:
        validar_caracteres_seguros(valor)
        return valor

    def create(self, validated_data: dict) -> Entrada:
        # usuario é injetado via perform_create(serializer.save(usuario=...)).
        usuario = validated_data.pop("usuario")
        return criar_entrada(
            usuario=usuario,
            valor=validated_data["valor"],
            fonte=validated_data["fonte"],
            descricao=validated_data["descricao"],
            data=validated_data["data"],
        )
