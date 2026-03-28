from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from financas.models import Categoria, Gasto

# ---------------------------------------------------------------------------
# Filtros de busca no endpoint de Gastos
# ---------------------------------------------------------------------------
#
# O endpoint de Gastos suporta filtros via query string que permitem ao
# frontend exibir subconjuntos dos registros do usuário. Esses filtros são
# combinados com o isolamento multi-usuário — um usuário nunca consegue
# filtrar dados de outro.
#
# Filtros testados:
# — `?categoria=<id>`: retorna apenas os gastos daquela categoria. Permite
#   ao usuário ver quanto gastou em Alimentação, Transporte, etc.
# — `?data__gte=<data>`: retorna gastos a partir de uma data (inclusive).
#   Útil para filtrar gastos do mês atual ou de um período específico.
# — `?valor__lte=<valor>`: retorna gastos com valor até o informado.
#   Útil para encontrar gastos pequenos abaixo de um certo teto.
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
def categoria(user: User) -> Categoria:
    return Categoria.objects.create(nome="Alimentação", usuario=user)


# ---------------------------------------------------------------------------
# Filtros — Gasto
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestGastoFiltros:
    def test_filtro_por_categoria(
        self, auth_client: APIClient, user: User, categoria: Categoria
    ) -> None:
        # Gasto na categoria fixture; gasto em outra categoria — filtra 1.
        Gasto.objects.create(
            descricao="A",
            valor=Decimal("10.00"),
            categoria=categoria,
            usuario=user,
            data=date.today(),
        )
        outra = Categoria.objects.create(nome="Outra", usuario=user)
        Gasto.objects.create(
            descricao="B",
            valor=Decimal("20.00"),
            categoria=outra,
            usuario=user,
            data=date.today(),
        )
        url = reverse("gasto-list") + f"?categoria={categoria.pk}"
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_filtro_por_data_gte(
        self, auth_client: APIClient, user: User, categoria: Categoria
    ) -> None:
        hoje = date.today()
        ontem = hoje - timedelta(days=1)
        Gasto.objects.create(
            descricao="Hoje",
            valor=Decimal("10.00"),
            categoria=categoria,
            usuario=user,
            data=hoje,
        )
        Gasto.objects.create(
            descricao="Ontem",
            valor=Decimal("10.00"),
            categoria=categoria,
            usuario=user,
            data=ontem,
        )
        url = reverse("gasto-list") + f"?data__gte={hoje.isoformat()}"
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_filtro_por_valor_lte(
        self, auth_client: APIClient, user: User, categoria: Categoria
    ) -> None:
        Gasto.objects.create(
            descricao="Barato",
            valor=Decimal("10.00"),
            categoria=categoria,
            usuario=user,
            data=date.today(),
        )
        Gasto.objects.create(
            descricao="Caro",
            valor=Decimal("500.00"),
            categoria=categoria,
            usuario=user,
            data=date.today(),
        )
        url = reverse("gasto-list") + "?valor__lte=100"
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
