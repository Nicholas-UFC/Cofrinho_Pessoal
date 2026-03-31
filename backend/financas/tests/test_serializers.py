from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from financas.models import Categoria, Entrada, Fonte, Gasto
from financas.serializers import (
    CategoriaSerializer,
    EntradaSerializer,
    FonteSerializer,
    GastoSerializer,
)

_factory = APIRequestFactory()


def _requisicao(usuario: User, metodo: str = "post") -> Request:
    req = getattr(_factory, metodo)("/")
    req.user = usuario
    return req


# ---------------------------------------------------------------------------
# Fixtures compartilhadas
# ---------------------------------------------------------------------------


@pytest.fixture
def user(db: None) -> User:
    return User.objects.create_user(username="testuser", password="pass123")


@pytest.fixture
def outro_user(db: None) -> User:
    return User.objects.create_user(username="outro", password="pass123")


@pytest.fixture
def categoria(user: User) -> Categoria:
    return Categoria.objects.create(nome="Alimentação", usuario=user)


@pytest.fixture
def fonte(user: User) -> Fonte:
    return Fonte.objects.create(nome="Salário", usuario=user)


# ---------------------------------------------------------------------------
# CategoriaSerializer
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestCategoriaSerializer:
    def test_criacao_valida(self, user: User) -> None:
        s = CategoriaSerializer(
            data={"nome": "Alimentação"},
            context={"request": _requisicao(user)},
        )
        assert s.is_valid(), s.errors

    def test_nome_duplicado_mesmo_usuario_invalido(
        self, user: User, categoria: Categoria
    ) -> None:
        s = CategoriaSerializer(
            data={"nome": "Alimentação"},
            context={"request": _requisicao(user)},
        )
        assert not s.is_valid()
        assert "nome" in s.errors

    def test_nome_duplicado_outro_usuario_valido(
        self,
        outro_user: User,
        categoria: Categoria,
    ) -> None:
        # Outro usuário pode ter categoria com o mesmo nome.
        s = CategoriaSerializer(
            data={"nome": "Alimentação"},
            context={"request": _requisicao(outro_user)},
        )
        assert s.is_valid(), s.errors

    def test_update_preserva_proprio_nome(
        self, user: User, categoria: Categoria
    ) -> None:
        # Atualizar mantendo o próprio nome não deve ser bloqueado.
        s = CategoriaSerializer(
            instance=categoria,
            data={"nome": "Alimentação"},
            context={"request": _requisicao(user, "put")},
        )
        assert s.is_valid(), s.errors

    def test_update_pega_nome_alheio_invalido(
        self, user: User, categoria: Categoria
    ) -> None:
        outra = Categoria.objects.create(nome="Transporte", usuario=user)
        s = CategoriaSerializer(
            instance=outra,
            data={"nome": "Alimentação"},
            context={"request": _requisicao(user, "put")},
        )
        assert not s.is_valid()
        assert "nome" in s.errors

    def test_usuario_excluido_da_saida(
        self, user: User, categoria: Categoria
    ) -> None:
        s = CategoriaSerializer(instance=categoria)
        assert "usuario" not in s.data

    def test_campos_read_only_ignorados_no_input(
        self, user: User, categoria: Categoria
    ) -> None:
        s = CategoriaSerializer(
            instance=categoria,
            data={
                "nome": "Outro",
                "id": 9999,
                "criado_em": "2000-01-01T00:00:00Z",
            },
            context={"request": _requisicao(user, "put")},
        )
        assert s.is_valid(), s.errors
        assert "id" not in s.validated_data
        assert "criado_em" not in s.validated_data


# ---------------------------------------------------------------------------
# FonteSerializer
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestFonteSerializer:
    def test_criacao_valida(self, user: User) -> None:
        s = FonteSerializer(
            data={"nome": "Freelance"},
            context={"request": _requisicao(user)},
        )
        assert s.is_valid(), s.errors

    def test_nome_duplicado_mesmo_usuario_invalido(
        self, user: User, fonte: Fonte
    ) -> None:
        s = FonteSerializer(
            data={"nome": "Salário"},
            context={"request": _requisicao(user)},
        )
        assert not s.is_valid()
        assert "nome" in s.errors

    def test_nome_duplicado_outro_usuario_valido(
        self,
        outro_user: User,
        fonte: Fonte,
    ) -> None:
        s = FonteSerializer(
            data={"nome": "Salário"},
            context={"request": _requisicao(outro_user)},
        )
        assert s.is_valid(), s.errors

    def test_update_preserva_proprio_nome(
        self, user: User, fonte: Fonte
    ) -> None:
        s = FonteSerializer(
            instance=fonte,
            data={"nome": "Salário"},
            context={"request": _requisicao(user, "put")},
        )
        assert s.is_valid(), s.errors

    def test_update_pega_nome_alheio_invalido(
        self, user: User, fonte: Fonte
    ) -> None:
        outra = Fonte.objects.create(nome="Freelance", usuario=user)
        s = FonteSerializer(
            instance=outra,
            data={"nome": "Salário"},
            context={"request": _requisicao(user, "put")},
        )
        assert not s.is_valid()
        assert "nome" in s.errors

    def test_usuario_excluido_da_saida(
        self, user: User, fonte: Fonte
    ) -> None:
        s = FonteSerializer(instance=fonte)
        assert "usuario" not in s.data


# ---------------------------------------------------------------------------
# GastoSerializer
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestGastoSerializer:
    def test_valor_positivo_valido(
        self, user: User, categoria: Categoria
    ) -> None:
        s = GastoSerializer(
            data={
                "descricao": "Supermercado",
                "valor": "150.00",
                "categoria": categoria.id,
                "data": str(date.today()),
            },
            context={"request": _requisicao(user)},
        )
        assert s.is_valid(), s.errors

    def test_valor_zero_invalido(
        self, user: User, categoria: Categoria
    ) -> None:
        s = GastoSerializer(
            data={
                "descricao": "Inválido",
                "valor": "0.00",
                "categoria": categoria.id,
                "data": str(date.today()),
            },
            context={"request": _requisicao(user)},
        )
        assert not s.is_valid()
        assert "valor" in s.errors

    def test_valor_negativo_invalido(
        self, user: User, categoria: Categoria
    ) -> None:
        s = GastoSerializer(
            data={
                "descricao": "Inválido",
                "valor": "-50.00",
                "categoria": categoria.id,
                "data": str(date.today()),
            },
            context={"request": _requisicao(user)},
        )
        assert not s.is_valid()
        assert "valor" in s.errors

    def test_usuario_excluido_da_saida(
        self, user: User, categoria: Categoria
    ) -> None:
        gasto = Gasto.objects.create(
            descricao="Café",
            valor=Decimal("10.00"),
            categoria=categoria,
            usuario=user,
            data=date.today(),
        )
        s = GastoSerializer(instance=gasto)
        assert "usuario" not in s.data

    def test_campo_categoria_nome_read_only(
        self, user: User, categoria: Categoria
    ) -> None:
        # categoria_nome é somente-leitura e não deve ser aceito no input.
        s = GastoSerializer(
            data={
                "descricao": "Café",
                "valor": "10.00",
                "categoria": categoria.id,
                "data": str(date.today()),
                "categoria_nome": "Tentativa de injeção",
            },
            context={"request": _requisicao(user)},
        )
        assert s.is_valid(), s.errors
        assert "categoria_nome" not in s.validated_data


# ---------------------------------------------------------------------------
# EntradaSerializer
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestEntradaSerializer:
    def test_valor_positivo_valido(
        self, user: User, fonte: Fonte
    ) -> None:
        s = EntradaSerializer(
            data={
                "descricao": "Salário",
                "valor": "3000.00",
                "fonte": fonte.id,
                "data": str(date.today()),
            },
            context={"request": _requisicao(user)},
        )
        assert s.is_valid(), s.errors

    def test_valor_zero_invalido(
        self, user: User, fonte: Fonte
    ) -> None:
        s = EntradaSerializer(
            data={
                "descricao": "Inválido",
                "valor": "0.00",
                "fonte": fonte.id,
                "data": str(date.today()),
            },
            context={"request": _requisicao(user)},
        )
        assert not s.is_valid()
        assert "valor" in s.errors

    def test_valor_negativo_invalido(
        self, user: User, fonte: Fonte
    ) -> None:
        s = EntradaSerializer(
            data={
                "descricao": "Inválido",
                "valor": "-100.00",
                "fonte": fonte.id,
                "data": str(date.today()),
            },
            context={"request": _requisicao(user)},
        )
        assert not s.is_valid()
        assert "valor" in s.errors

    def test_usuario_excluido_da_saida(
        self, user: User, fonte: Fonte
    ) -> None:
        entrada = Entrada.objects.create(
            descricao="Salário",
            valor=Decimal("3000.00"),
            fonte=fonte,
            usuario=user,
            data=date.today(),
        )
        s = EntradaSerializer(instance=entrada)
        assert "usuario" not in s.data

    def test_campo_fonte_nome_read_only(
        self, user: User, fonte: Fonte
    ) -> None:
        # fonte_nome é somente-leitura e não deve ser aceito no input.
        s = EntradaSerializer(
            data={
                "descricao": "Salário",
                "valor": "3000.00",
                "fonte": fonte.id,
                "data": str(date.today()),
                "fonte_nome": "Tentativa de injeção",
            },
            context={"request": _requisicao(user)},
        )
        assert s.is_valid(), s.errors
        assert "fonte_nome" not in s.validated_data
