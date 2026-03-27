import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

# ---------------------------------------------------------------------------
# Autenticação — proteção de endpoints sem token JWT
# ---------------------------------------------------------------------------
#
# Todos os endpoints da API financeira são protegidos por JWT. Um cliente
# que não envie o header `Authorization: Bearer <token>` deve receber 401
# em qualquer endpoint — independentemente do método HTTP.
#
# Este arquivo verifica essa barreira para os quatro recursos principais:
# categorias, fontes, gastos e entradas. O objetivo é garantir que nenhum
# endpoint foi acidentalmente deixado sem autenticação, o que abriria uma
# brecha de segurança onde dados financeiros privados ficariam expostos.
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


# ---------------------------------------------------------------------------
# Autenticação — sem token deve retornar 401
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestAutenticacao:
    def test_categorias_sem_token_retorna_401(self, client: APIClient) -> None:
        response = client.get(reverse("categoria-list"))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_fontes_sem_token_retorna_401(self, client: APIClient) -> None:
        response = client.get(reverse("fonte-list"))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_gastos_sem_token_retorna_401(self, client: APIClient) -> None:
        response = client.get(reverse("gasto-list"))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_entradas_sem_token_retorna_401(self, client: APIClient) -> None:
        response = client.get(reverse("entrada-list"))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
