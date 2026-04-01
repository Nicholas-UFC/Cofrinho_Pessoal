from rest_framework_simplejwt.tokens import RefreshToken
from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from financas.models import Entrada, Fonte

# ---------------------------------------------------------------------------
# Filtros de busca no endpoint de Entradas
# ---------------------------------------------------------------------------
#
# O endpoint de Entradas suporta filtros via query string que permitem ao
# frontend e ao bot exibir apenas os registros relevantes para uma consulta.
# Esta suíte verifica que os filtros retornam exatamente os registros
# esperados e ignoram os demais:
#
# — `?fonte=<id>`: filtra entradas por fonte específica. Útil para analisar
#   quanto veio de uma determinada fonte (ex: somente salário vs. freelance).
# — `?valor__gte=<valor>`: filtra entradas com valor maior ou igual ao
#   informado. Útil para identificar entradas acima de um certo patamar.
#
# Todos os filtros operam apenas sobre os dados do usuário autenticado —
# o isolamento multi-usuário já é garantido pelo queryset base do viewset.
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
    token = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
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
