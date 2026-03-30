from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.db import connection
from django.test.utils import CaptureQueriesContext

from financas.models import Categoria, Entrada, Fonte, Gasto
from whatsapp.services import _listar_categorias, _listar_fontes, _obter_resumo

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def user(db: None) -> User:
    return User.objects.create_user(username="testuser", password="pass123")


# ---------------------------------------------------------------------------
# N+1 — query count deve ser constante independente do volume
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestQueriesListarCategorias:
    def test_sem_n_plus_1(self, user: User) -> None:
        Categoria.objects.create(nome="Cat1", usuario=user)
        with CaptureQueriesContext(connection) as ctx_1:
            _listar_categorias(user)
        n_com_1 = len(ctx_1)

        for i in range(2, 7):
            Categoria.objects.create(nome=f"Cat{i}", usuario=user)
        with CaptureQueriesContext(connection) as ctx_6:
            _listar_categorias(user)
        n_com_6 = len(ctx_6)

        assert n_com_1 == n_com_6, (
            f"N+1 em _listar_categorias: {n_com_1} queries com 1 item, "
            f"{n_com_6} queries com 6 itens"
        )


@pytest.mark.django_db
class TestQueriesListarFontes:
    def test_sem_n_plus_1(self, user: User) -> None:
        Fonte.objects.create(nome="Fonte1", usuario=user)
        with CaptureQueriesContext(connection) as ctx_1:
            _listar_fontes(user)
        n_com_1 = len(ctx_1)

        for i in range(2, 7):
            Fonte.objects.create(nome=f"Fonte{i}", usuario=user)
        with CaptureQueriesContext(connection) as ctx_6:
            _listar_fontes(user)
        n_com_6 = len(ctx_6)

        assert n_com_1 == n_com_6, (
            f"N+1 em _listar_fontes: {n_com_1} queries com 1 item, "
            f"{n_com_6} queries com 6 itens"
        )


@pytest.mark.django_db
class TestQueriesObterResumo:
    def test_sem_n_plus_1(self, user: User) -> None:
        categoria = Categoria.objects.create(nome="Cat", usuario=user)
        fonte = Fonte.objects.create(nome="Fonte", usuario=user)

        Gasto.objects.create(
            descricao="G0",
            valor=Decimal("10.00"),
            categoria=categoria,
            usuario=user,
            data=date.today(),
        )
        Entrada.objects.create(
            descricao="E0",
            valor=Decimal("100.00"),
            fonte=fonte,
            usuario=user,
            data=date.today(),
        )
        with CaptureQueriesContext(connection) as ctx_2:
            _obter_resumo(user)
        n_com_2 = len(ctx_2)

        for i in range(1, 6):
            Gasto.objects.create(
                descricao=f"G{i}",
                valor=Decimal("10.00"),
                categoria=categoria,
                usuario=user,
                data=date.today(),
            )
            Entrada.objects.create(
                descricao=f"E{i}",
                valor=Decimal("100.00"),
                fonte=fonte,
                usuario=user,
                data=date.today(),
            )
        with CaptureQueriesContext(connection) as ctx_12:
            _obter_resumo(user)
        n_com_12 = len(ctx_12)

        assert n_com_2 == n_com_12, (
            f"N+1 em _obter_resumo: {n_com_2} queries com 2 registros, "
            f"{n_com_12} queries com 12 registros"
        )
