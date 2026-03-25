from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from financas.models import Entrada, Fonte

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
def fonte(user: User) -> Fonte:
    return Fonte.objects.create(nome="Salário", usuario=user)


# ---------------------------------------------------------------------------
# Filtros — Entrada
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestEntradaFiltros:
    def test_filtro_por_fonte(
        self, auth_client: APIClient, user: User, fonte: Fonte
    ) -> None:
        Entrada.objects.create(
            descricao="A",
            valor=Decimal("100.00"),
            fonte=fonte,
            usuario=user,
            data=date.today(),
        )
        outra = Fonte.objects.create(nome="Outra", usuario=user)
        Entrada.objects.create(
            descricao="B",
            valor=Decimal("200.00"),
            fonte=outra,
            usuario=user,
            data=date.today(),
        )
        url = reverse("entrada-list") + f"?fonte={fonte.pk}"
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_filtro_por_valor_gte(
        self, auth_client: APIClient, user: User, fonte: Fonte
    ) -> None:
        Entrada.objects.create(
            descricao="Pequena",
            valor=Decimal("50.00"),
            fonte=fonte,
            usuario=user,
            data=date.today(),
        )
        Entrada.objects.create(
            descricao="Grande",
            valor=Decimal("5000.00"),
            fonte=fonte,
            usuario=user,
            data=date.today(),
        )
        url = reverse("entrada-list") + "?valor__gte=1000"
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
