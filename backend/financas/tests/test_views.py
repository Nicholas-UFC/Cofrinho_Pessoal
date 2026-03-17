from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from financas.models import Categoria, Entrada, Fonte, Gasto

# ---------------------------------------------------------------------------
# Fixtures compartilhadas
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
def categoria(db: None) -> Categoria:
    return Categoria.objects.create(nome="Alimentação")


@pytest.fixture
def fonte(db: None) -> Fonte:
    return Fonte.objects.create(nome="Salário")


@pytest.fixture
def gasto(db: None, categoria: Categoria) -> Gasto:
    return Gasto.objects.create(
        descricao="Supermercado",
        valor=Decimal("150.00"),
        categoria=categoria,
        data=date.today(),
    )


@pytest.fixture
def entrada(db: None, fonte: Fonte) -> Entrada:
    return Entrada.objects.create(
        descricao="Salário Janeiro",
        valor=Decimal("3000.00"),
        fonte=fonte,
        data=date.today(),
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


# ---------------------------------------------------------------------------
# Categoria
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestCategoriaViewSet:
    def test_list(self, auth_client: APIClient, categoria: Categoria) -> None:
        response = auth_client.get(reverse("categoria-list"))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_create(self, auth_client: APIClient) -> None:
        response = auth_client.post(
            reverse("categoria-list"), {"nome": "Transporte"}
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert Categoria.objects.filter(nome="Transporte").exists()

    def test_retrieve(
        self, auth_client: APIClient, categoria: Categoria
    ) -> None:
        url = reverse("categoria-detail", args=[categoria.pk])
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["nome"] == "Alimentação"

    def test_update(
        self, auth_client: APIClient, categoria: Categoria
    ) -> None:
        url = reverse("categoria-detail", args=[categoria.pk])
        response = auth_client.put(url, {"nome": "Lazer"})
        assert response.status_code == status.HTTP_200_OK
        categoria.refresh_from_db()
        assert categoria.nome == "Lazer"

    def test_destroy(
        self, auth_client: APIClient, categoria: Categoria
    ) -> None:
        url = reverse("categoria-detail", args=[categoria.pk])
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Categoria.objects.filter(pk=categoria.pk).exists()

    def test_create_nome_duplicado_retorna_400(
        self, auth_client: APIClient, categoria: Categoria
    ) -> None:
        response = auth_client.post(
            reverse("categoria-list"), {"nome": "Alimentação"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ---------------------------------------------------------------------------
# Fonte
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestFonteViewSet:
    def test_list(self, auth_client: APIClient, fonte: Fonte) -> None:
        response = auth_client.get(reverse("fonte-list"))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_create(self, auth_client: APIClient) -> None:
        response = auth_client.post(
            reverse("fonte-list"), {"nome": "Freelance"}
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert Fonte.objects.filter(nome="Freelance").exists()

    def test_retrieve(self, auth_client: APIClient, fonte: Fonte) -> None:
        url = reverse("fonte-detail", args=[fonte.pk])
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["nome"] == "Salário"

    def test_update(self, auth_client: APIClient, fonte: Fonte) -> None:
        url = reverse("fonte-detail", args=[fonte.pk])
        response = auth_client.put(url, {"nome": "Bônus"})
        assert response.status_code == status.HTTP_200_OK
        fonte.refresh_from_db()
        assert fonte.nome == "Bônus"

    def test_destroy(self, auth_client: APIClient, fonte: Fonte) -> None:
        url = reverse("fonte-detail", args=[fonte.pk])
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Fonte.objects.filter(pk=fonte.pk).exists()

    def test_create_nome_duplicado_retorna_400(
        self, auth_client: APIClient, fonte: Fonte
    ) -> None:
        response = auth_client.post(reverse("fonte-list"), {"nome": "Salário"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ---------------------------------------------------------------------------
# Gasto
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestGastoViewSet:
    def test_list(self, auth_client: APIClient, gasto: Gasto) -> None:
        response = auth_client.get(reverse("gasto-list"))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_create(
        self, auth_client: APIClient, categoria: Categoria
    ) -> None:
        response = auth_client.post(
            reverse("gasto-list"),
            {
                "descricao": "Farmácia",
                "valor": "45.50",
                "categoria": categoria.pk,
                "data": date.today().isoformat(),
            },
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_retrieve(self, auth_client: APIClient, gasto: Gasto) -> None:
        url = reverse("gasto-detail", args=[gasto.pk])
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["descricao"] == "Supermercado"

    def test_update(
        self, auth_client: APIClient, gasto: Gasto, categoria: Categoria
    ) -> None:
        url = reverse("gasto-detail", args=[gasto.pk])
        response = auth_client.put(
            url,
            {
                "descricao": "Mercado",
                "valor": "200.00",
                "categoria": categoria.pk,
                "data": date.today().isoformat(),
            },
        )
        assert response.status_code == status.HTTP_200_OK
        gasto.refresh_from_db()
        assert gasto.descricao == "Mercado"

    def test_destroy(self, auth_client: APIClient, gasto: Gasto) -> None:
        url = reverse("gasto-detail", args=[gasto.pk])
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Gasto.objects.filter(pk=gasto.pk).exists()

    def test_create_valor_negativo_retorna_400(
        self, auth_client: APIClient, categoria: Categoria
    ) -> None:
        response = auth_client.post(
            reverse("gasto-list"),
            {
                "descricao": "Inválido",
                "valor": "-10.00",
                "categoria": categoria.pk,
                "data": date.today().isoformat(),
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ---------------------------------------------------------------------------
# Entrada
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestEntradaViewSet:
    def test_list(self, auth_client: APIClient, entrada: Entrada) -> None:
        response = auth_client.get(reverse("entrada-list"))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_create(self, auth_client: APIClient, fonte: Fonte) -> None:
        response = auth_client.post(
            reverse("entrada-list"),
            {
                "descricao": "Freelance",
                "valor": "500.00",
                "fonte": fonte.pk,
                "data": date.today().isoformat(),
            },
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_retrieve(self, auth_client: APIClient, entrada: Entrada) -> None:
        url = reverse("entrada-detail", args=[entrada.pk])
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["descricao"] == "Salário Janeiro"

    def test_update(
        self, auth_client: APIClient, entrada: Entrada, fonte: Fonte
    ) -> None:
        url = reverse("entrada-detail", args=[entrada.pk])
        response = auth_client.put(
            url,
            {
                "descricao": "Salário Fevereiro",
                "valor": "3200.00",
                "fonte": fonte.pk,
                "data": date.today().isoformat(),
            },
        )
        assert response.status_code == status.HTTP_200_OK
        entrada.refresh_from_db()
        assert entrada.descricao == "Salário Fevereiro"

    def test_destroy(self, auth_client: APIClient, entrada: Entrada) -> None:
        url = reverse("entrada-detail", args=[entrada.pk])
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Entrada.objects.filter(pk=entrada.pk).exists()

    def test_create_valor_negativo_retorna_400(
        self, auth_client: APIClient, fonte: Fonte
    ) -> None:
        response = auth_client.post(
            reverse("entrada-list"),
            {
                "descricao": "Inválido",
                "valor": "-10.00",
                "fonte": fonte.pk,
                "data": date.today().isoformat(),
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
