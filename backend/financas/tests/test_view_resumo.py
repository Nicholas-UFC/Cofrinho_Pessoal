from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from financas.models import Categoria, Entrada, Fonte, Gasto

# ---------------------------------------------------------------------------
# Endpoint de resumo financeiro mensal
# ---------------------------------------------------------------------------
#
# O endpoint `/api/resumo/` agrega os dados financeiros do usuário autenticado
# e retorna um snapshot do mês atual: total de entradas, total de gastos,
# saldo (entradas - gastos) e gastos agrupados por categoria.
#
# Esta suíte verifica:
# — Sem dados, todos os totais retornam zero.
# — Com entradas e gastos, o saldo é calculado corretamente.
# — Os gastos são agrupados por categoria com o total correto por categoria,
#   permitindo ao frontend exibir um breakdown de onde o dinheiro foi gasto.
# — Sem token, o endpoint retorna 401 — o resumo é sempre privado.
# — Isolamento multi-usuário: entradas e gastos de outro usuário não
#   aparecem no resumo do usuário autenticado, mesmo que sejam do mesmo mês.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def client() -> APIClient:
    # Cliente da API sem autenticação — usado para testar rotas protegidas.
    return APIClient()


@pytest.fixture
def user(db: None) -> User:
    return User.objects.create_user(
        username="testuser", password="testpass123"
    )


@pytest.fixture
def auth_client(client: APIClient, user: User) -> APIClient:
    # Cliente autenticado via JWT para os testes normais.
    response = client.post(
        "/api/token/",
        {"username": "testuser", "password": "testpass123"},
    )
    token = response.data["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.fixture
def outro_user(db: None) -> User:
    # Segundo usuário para testes de isolamento multi-usuário.
    return User.objects.create_user(
        username="outrouser", password="outropass123"
    )


@pytest.fixture
def categoria(user: User) -> Categoria:
    return Categoria.objects.create(nome="Alimentação", usuario=user)


@pytest.fixture
def fonte(user: User) -> Fonte:
    return Fonte.objects.create(nome="Salário", usuario=user)


# ---------------------------------------------------------------------------
# Resumo financeiro
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestResumo:
    def test_resumo_sem_dados_retorna_zeros(
        self, auth_client: APIClient
    ) -> None:
        response = auth_client.get(reverse("resumo"))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["total_entradas"] == 0
        assert response.data["total_gastos"] == 0
        assert response.data["saldo"] == 0

    def test_resumo_calcula_saldo(
        self,
        auth_client: APIClient,
        user: User,
        categoria: Categoria,
        fonte: Fonte,
    ) -> None:
        Entrada.objects.create(
            descricao="Salário",
            valor=Decimal("3000.00"),
            fonte=fonte,
            usuario=user,
            data=date.today(),
        )
        Gasto.objects.create(
            descricao="Aluguel",
            valor=Decimal("1000.00"),
            categoria=categoria,
            usuario=user,
            data=date.today(),
        )
        response = auth_client.get(reverse("resumo"))
        assert response.data["total_entradas"] == Decimal("3000.00")
        assert response.data["total_gastos"] == Decimal("1000.00")
        assert response.data["saldo"] == Decimal("2000.00")

    # --- Agrupamento por categoria ---

    def test_resumo_agrupa_gastos_por_categoria(
        self,
        auth_client: APIClient,
        user: User,
        categoria: Categoria,
    ) -> None:
        outra = Categoria.objects.create(nome="Transporte", usuario=user)
        Gasto.objects.create(
            descricao="Mercado",
            valor=Decimal("200.00"),
            categoria=categoria,
            usuario=user,
            data=date.today(),
        )
        Gasto.objects.create(
            descricao="Uber",
            valor=Decimal("50.00"),
            categoria=outra,
            usuario=user,
            data=date.today(),
        )
        response = auth_client.get(reverse("resumo"))
        por_categoria = {
            item["categoria__nome"]: item["total"]
            for item in response.data["gastos_por_categoria"]
        }
        assert por_categoria["Alimentação"] == Decimal("200.00")
        assert por_categoria["Transporte"] == Decimal("50.00")

    def test_resumo_sem_token_retorna_401(self, client: APIClient) -> None:
        response = client.get(reverse("resumo"))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # --- Isolamento multi-usuário ---

    def test_resumo_nao_inclui_entradas_de_outro_usuario(
        self,
        auth_client: APIClient,
        user: User,
        fonte: Fonte,
        outro_user: User,
    ) -> None:
        outra_fonte = Fonte.objects.create(
            nome="Freelance", usuario=outro_user
        )
        Entrada.objects.create(
            descricao="Salário",
            valor=Decimal("3000.00"),
            fonte=fonte,
            usuario=user,
            data=date.today(),
        )
        Entrada.objects.create(
            descricao="Renda extra",
            valor=Decimal("99999.00"),
            fonte=outra_fonte,
            usuario=outro_user,
            data=date.today(),
        )
        response = auth_client.get(reverse("resumo"))
        assert response.data["total_entradas"] == Decimal("3000.00")

    def test_resumo_nao_inclui_gastos_de_outro_usuario(
        self,
        auth_client: APIClient,
        user: User,
        categoria: Categoria,
        outro_user: User,
    ) -> None:
        outra_cat = Categoria.objects.create(
            nome="Alimentação", usuario=outro_user
        )
        Gasto.objects.create(
            descricao="Aluguel",
            valor=Decimal("1000.00"),
            categoria=categoria,
            usuario=user,
            data=date.today(),
        )
        Gasto.objects.create(
            descricao="Compra",
            valor=Decimal("99999.00"),
            categoria=outra_cat,
            usuario=outro_user,
            data=date.today(),
        )
        response = auth_client.get(reverse("resumo"))
        assert response.data["total_gastos"] == Decimal("1000.00")
