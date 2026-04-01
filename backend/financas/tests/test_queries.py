from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.db import connection
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APIClient

from financas.models import Categoria, Entrada, Fonte, Gasto

# ---------------------------------------------------------------------------
# Fixtures compartilhadas
# ---------------------------------------------------------------------------


@pytest.fixture
def user(db: None) -> User:
    return User.objects.create_user(
        username="testuser", password="testpass123"
    )


@pytest.fixture
def auth_client(user: User) -> APIClient:
    from rest_framework_simplejwt.tokens import RefreshToken

    c = APIClient()
    token = RefreshToken.for_user(user)
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
    return c


@pytest.fixture
def categoria(user: User) -> Categoria:
    return Categoria.objects.create(nome="Alimentação", usuario=user)


@pytest.fixture
def fonte(user: User) -> Fonte:
    return Fonte.objects.create(nome="Salário", usuario=user)


def _criar_gastos(n: int, usuario: User, categoria: Categoria) -> None:
    for i in range(n):
        Gasto.objects.create(
            descricao=f"Gasto {i}",
            valor=Decimal("10.00"),
            categoria=categoria,
            usuario=usuario,
            data=date.today(),
        )


def _criar_entradas(n: int, usuario: User, fonte: Fonte) -> None:
    for i in range(n):
        Entrada.objects.create(
            descricao=f"Entrada {i}",
            valor=Decimal("100.00"),
            fonte=fonte,
            usuario=usuario,
            data=date.today(),
        )


# ---------------------------------------------------------------------------
# Testes de N+1 — query count deve ser constante independente do volume
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestQueriesGastos:
    def test_sem_n_plus_1(
        self,
        auth_client: APIClient,
        user: User,
        categoria: Categoria,
    ) -> None:
        _criar_gastos(1, user, categoria)
        with CaptureQueriesContext(connection) as ctx_1:
            auth_client.get("/api/financas/gastos/")
        n_com_1 = len(ctx_1)

        _criar_gastos(5, user, categoria)
        with CaptureQueriesContext(connection) as ctx_6:
            auth_client.get("/api/financas/gastos/")
        n_com_6 = len(ctx_6)

        assert n_com_1 == n_com_6, (
            f"N+1 em gastos: {n_com_1} queries com 1 registro, "
            f"{n_com_6} queries com 6 registros"
        )


@pytest.mark.django_db
class TestQueriesEntradas:
    def test_sem_n_plus_1(
        self,
        auth_client: APIClient,
        user: User,
        fonte: Fonte,
    ) -> None:
        _criar_entradas(1, user, fonte)
        with CaptureQueriesContext(connection) as ctx_1:
            auth_client.get("/api/financas/entradas/")
        n_com_1 = len(ctx_1)

        _criar_entradas(5, user, fonte)
        with CaptureQueriesContext(connection) as ctx_6:
            auth_client.get("/api/financas/entradas/")
        n_com_6 = len(ctx_6)

        assert n_com_1 == n_com_6, (
            f"N+1 em entradas: {n_com_1} queries com 1 registro, "
            f"{n_com_6} queries com 6 registros"
        )


@pytest.mark.django_db
class TestQueriesCategorias:
    def test_sem_n_plus_1(
        self,
        auth_client: APIClient,
        user: User,
    ) -> None:
        Categoria.objects.create(nome="Cat1", usuario=user)
        with CaptureQueriesContext(connection) as ctx_1:
            auth_client.get("/api/financas/categorias/")
        n_com_1 = len(ctx_1)

        for i in range(2, 7):
            Categoria.objects.create(nome=f"Cat{i}", usuario=user)
        with CaptureQueriesContext(connection) as ctx_6:
            auth_client.get("/api/financas/categorias/")
        n_com_6 = len(ctx_6)

        assert n_com_1 == n_com_6, (
            f"N+1 em categorias: {n_com_1} queries com 1 registro, "
            f"{n_com_6} queries com 6 registros"
        )


@pytest.mark.django_db
class TestQueriesFontes:
    def test_sem_n_plus_1(
        self,
        auth_client: APIClient,
        user: User,
    ) -> None:
        Fonte.objects.create(nome="Fonte1", usuario=user)
        with CaptureQueriesContext(connection) as ctx_1:
            auth_client.get("/api/financas/fontes/")
        n_com_1 = len(ctx_1)

        for i in range(2, 7):
            Fonte.objects.create(nome=f"Fonte{i}", usuario=user)
        with CaptureQueriesContext(connection) as ctx_6:
            auth_client.get("/api/financas/fontes/")
        n_com_6 = len(ctx_6)

        assert n_com_1 == n_com_6, (
            f"N+1 em fontes: {n_com_1} queries com 1 registro, "
            f"{n_com_6} queries com 6 registros"
        )


@pytest.mark.django_db
class TestQueriesResumo:
    def test_sem_n_plus_1(
        self,
        auth_client: APIClient,
        user: User,
        categoria: Categoria,
        fonte: Fonte,
    ) -> None:
        _criar_gastos(1, user, categoria)
        _criar_entradas(1, user, fonte)
        with CaptureQueriesContext(connection) as ctx_2:
            auth_client.get("/api/financas/resumo/")
        n_com_2 = len(ctx_2)

        _criar_gastos(5, user, categoria)
        _criar_entradas(5, user, fonte)
        with CaptureQueriesContext(connection) as ctx_12:
            auth_client.get("/api/financas/resumo/")
        n_com_12 = len(ctx_12)

        assert n_com_2 == n_com_12, (
            f"N+1 em resumo: {n_com_2} queries com 2 registros, "
            f"{n_com_12} queries com 12 registros"
        )
