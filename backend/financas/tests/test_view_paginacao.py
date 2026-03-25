from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from financas.models import Categoria, Gasto

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
# Paginação
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestPaginacao:
    def test_resposta_paginada_tem_estrutura_correta(
        self, auth_client: APIClient, user: User, categoria: Categoria
    ) -> None:
        # Cria 1 gasto e verifica os campos de paginação na resposta.
        Gasto.objects.create(
            descricao="Teste",
            valor=Decimal("10.00"),
            categoria=categoria,
            usuario=user,
            data=date.today(),
        )
        response = auth_client.get(reverse("gasto-list"))
        assert response.status_code == status.HTTP_200_OK
        assert "count" in response.data
        assert "next" in response.data
        assert "previous" in response.data
        assert "results" in response.data

    def test_count_reflete_total_de_registros(
        self, auth_client: APIClient, user: User, categoria: Categoria
    ) -> None:
        for i in range(3):
            Gasto.objects.create(
                descricao=f"Gasto {i}",
                valor=Decimal("10.00"),
                categoria=categoria,
                usuario=user,
                data=date.today(),
            )
        response = auth_client.get(reverse("gasto-list"))
        assert response.data["count"] == 3
