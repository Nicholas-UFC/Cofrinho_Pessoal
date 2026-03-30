from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from financas.models import Categoria, Entrada, Fonte, Gasto

# ---------------------------------------------------------------------------
# Ordenação padrão dos endpoints
#
# Cada model define um `ordering` na Meta. Estes testes garantem que a API
# respeita esse ordenamento padrão, protegendo contra remoções acidentais
# do campo `ordering` nos models.
#
# Gastos e Entradas → ordenados por -data (mais recente primeiro)
# Categorias e Fontes → ordenados por nome (alfabético)
# ---------------------------------------------------------------------------


@pytest.fixture
def user(db: None) -> User:
    return User.objects.create_user(
        username="testuser", password="testpass123"
    )


@pytest.fixture
def auth_client(user: User) -> APIClient:
    c = APIClient()
    response = c.post(
        "/api/token/",
        {"username": "testuser", "password": "testpass123"},
    )
    token = response.data["access"]
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return c


@pytest.fixture
def categoria(user: User) -> Categoria:
    return Categoria.objects.create(nome="Compras", usuario=user)


@pytest.fixture
def fonte(user: User) -> Fonte:
    return Fonte.objects.create(nome="Salario", usuario=user)


# ---------------------------------------------------------------------------
# Gastos — ordenados por -data
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestOrdenacaoGastos:
    def test_lista_mais_recente_primeiro(
        self,
        auth_client: APIClient,
        user: User,
        categoria: Categoria,
    ) -> None:
        hoje = date.today()
        ontem = hoje - timedelta(days=1)
        anteontem = hoje - timedelta(days=2)

        Gasto.objects.create(
            descricao="Antigo",
            valor=Decimal("10.00"),
            categoria=categoria,
            usuario=user,
            data=anteontem,
        )
        Gasto.objects.create(
            descricao="Recente",
            valor=Decimal("20.00"),
            categoria=categoria,
            usuario=user,
            data=hoje,
        )
        Gasto.objects.create(
            descricao="Meio",
            valor=Decimal("30.00"),
            categoria=categoria,
            usuario=user,
            data=ontem,
        )

        response = auth_client.get(reverse("gasto-list"))
        assert response.status_code == status.HTTP_200_OK
        datas = [r["data"] for r in response.data["results"]]
        assert datas == sorted(datas, reverse=True)

    def test_primeiro_item_e_o_mais_recente(
        self,
        auth_client: APIClient,
        user: User,
        categoria: Categoria,
    ) -> None:
        hoje = date.today()
        ontem = hoje - timedelta(days=1)

        Gasto.objects.create(
            descricao="Ontem",
            valor=Decimal("10.00"),
            categoria=categoria,
            usuario=user,
            data=ontem,
        )
        Gasto.objects.create(
            descricao="Hoje",
            valor=Decimal("20.00"),
            categoria=categoria,
            usuario=user,
            data=hoje,
        )

        response = auth_client.get(reverse("gasto-list"))
        primeiro = response.data["results"][0]
        assert primeiro["descricao"] == "Hoje"


# ---------------------------------------------------------------------------
# Entradas — ordenadas por -data
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestOrdenacaoEntradas:
    def test_lista_mais_recente_primeiro(
        self,
        auth_client: APIClient,
        user: User,
        fonte: Fonte,
    ) -> None:
        hoje = date.today()
        ontem = hoje - timedelta(days=1)
        anteontem = hoje - timedelta(days=2)

        Entrada.objects.create(
            descricao="Antiga",
            valor=Decimal("100.00"),
            fonte=fonte,
            usuario=user,
            data=anteontem,
        )
        Entrada.objects.create(
            descricao="Recente",
            valor=Decimal("200.00"),
            fonte=fonte,
            usuario=user,
            data=hoje,
        )
        Entrada.objects.create(
            descricao="Meio",
            valor=Decimal("300.00"),
            fonte=fonte,
            usuario=user,
            data=ontem,
        )

        response = auth_client.get(reverse("entrada-list"))
        assert response.status_code == status.HTTP_200_OK
        datas = [r["data"] for r in response.data["results"]]
        assert datas == sorted(datas, reverse=True)

    def test_primeiro_item_e_o_mais_recente(
        self,
        auth_client: APIClient,
        user: User,
        fonte: Fonte,
    ) -> None:
        hoje = date.today()
        ontem = hoje - timedelta(days=1)

        Entrada.objects.create(
            descricao="Ontem",
            valor=Decimal("100.00"),
            fonte=fonte,
            usuario=user,
            data=ontem,
        )
        Entrada.objects.create(
            descricao="Hoje",
            valor=Decimal("200.00"),
            fonte=fonte,
            usuario=user,
            data=hoje,
        )

        response = auth_client.get(reverse("entrada-list"))
        primeiro = response.data["results"][0]
        assert primeiro["descricao"] == "Hoje"


# ---------------------------------------------------------------------------
# Categorias — ordenadas por nome (alfabético)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestOrdenacaoCategorias:
    def test_lista_em_ordem_alfabetica(
        self, auth_client: APIClient, user: User
    ) -> None:
        Categoria.objects.create(nome="Moradia", usuario=user)
        Categoria.objects.create(nome="Compras", usuario=user)
        Categoria.objects.create(nome="Lazer", usuario=user)

        response = auth_client.get(reverse("categoria-list"))
        assert response.status_code == status.HTTP_200_OK
        nomes = [r["nome"] for r in response.data]
        assert nomes == sorted(nomes)

    def test_primeiro_item_e_o_primeiro_alfabeticamente(
        self, auth_client: APIClient, user: User
    ) -> None:
        Categoria.objects.create(nome="Moradia", usuario=user)
        Categoria.objects.create(nome="Compras", usuario=user)

        response = auth_client.get(reverse("categoria-list"))
        assert response.data[0]["nome"] == "Compras"


# ---------------------------------------------------------------------------
# Fontes — ordenadas por nome (alfabético)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestOrdenacaoFontes:
    def test_lista_em_ordem_alfabetica(
        self, auth_client: APIClient, user: User
    ) -> None:
        Fonte.objects.create(nome="Salario", usuario=user)
        Fonte.objects.create(nome="Freelance", usuario=user)
        Fonte.objects.create(nome="Aluguel", usuario=user)

        response = auth_client.get(reverse("fonte-list"))
        assert response.status_code == status.HTTP_200_OK
        nomes = [r["nome"] for r in response.data]
        assert nomes == sorted(nomes)

    def test_primeiro_item_e_o_primeiro_alfabeticamente(
        self, auth_client: APIClient, user: User
    ) -> None:
        Fonte.objects.create(nome="Salario", usuario=user)
        Fonte.objects.create(nome="Aluguel", usuario=user)

        response = auth_client.get(reverse("fonte-list"))
        assert response.data[0]["nome"] == "Aluguel"
