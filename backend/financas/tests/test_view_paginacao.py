from rest_framework_simplejwt.tokens import RefreshToken
from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from financas.models import Categoria, Fonte, Gasto

# ---------------------------------------------------------------------------
# Paginação e estrutura de resposta dos endpoints
# ---------------------------------------------------------------------------
#
# Esta suíte verifica duas coisas distintas relacionadas ao formato de resposta
# da API:
#
# 1. PAGINAÇÃO EM GASTO E ENTRADA: os endpoints paginados devem retornar um
#    objeto com os campos `count`, `next`, `previous` e `results`. O campo
#    `count` deve refletir o número total de registros do usuário, não apenas
#    os da página atual.
#
# 2. LISTA PLANA EM CATEGORIA E FONTE (regressão): esses dois endpoints não
#    são paginados — devem retornar uma lista Python simples, não um dict com
#    `{count, next, previous, results}`. Isso é necessário porque o frontend
#    usa `categorias.map(...)` diretamente na resposta; se receber um dict
#    paginado, quebra com "TypeError: categorias.map is not a function".
#    O bug foi introduzido quando DEFAULT_PAGINATION_CLASS foi configurado
#    globalmente, afetando endpoints que deveriam permanecer sem paginação.
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


# ---------------------------------------------------------------------------
# Regressão — lista plana em Categoria e Fonte
# ---------------------------------------------------------------------------


@pytest.fixture
def fonte(user: User) -> Fonte:
    return Fonte.objects.create(nome="Salário", usuario=user)


@pytest.mark.django_db
class TestCategoriaFonteSemPaginacao:
    def test_categorias_retorna_lista_plana(
        self, auth_client: APIClient, categoria: Categoria
    ) -> None:
        # Regressão: deve ser lista, não dict paginado {count, results}.
        response = auth_client.get(reverse("categoria-list"))
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)

    def test_fontes_retorna_lista_plana(
        self, auth_client: APIClient, fonte: Fonte
    ) -> None:
        # Regressão: deve ser lista, não dict paginado {count, results}.
        response = auth_client.get(reverse("fonte-list"))
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
