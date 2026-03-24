from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from financas.models import Categoria, Entrada, Fonte, Gasto


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
def gasto(user: User, categoria: Categoria) -> Gasto:
    return Gasto.objects.create(
        descricao="Supermercado",
        valor=Decimal("150.00"),
        categoria=categoria,
        usuario=user,
        data=date.today(),
    )


# ---------------------------------------------------------------------------
# Gasto
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestGastoViewSet:
    def test_list(self, auth_client: APIClient, gasto: Gasto) -> None:
        response = auth_client.get(reverse("gasto-list"))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

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

    def test_create_valor_zero_retorna_400(
        self, auth_client: APIClient, categoria: Categoria
    ) -> None:
        response = auth_client.post(
            reverse("gasto-list"),
            {
                "descricao": "Inválido",
                "valor": "0.00",
                "categoria": categoria.pk,
                "data": date.today().isoformat(),
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_sem_descricao_retorna_400(
        self, auth_client: APIClient, categoria: Categoria
    ) -> None:
        response = auth_client.post(
            reverse("gasto-list"),
            {
                "valor": "50.00",
                "categoria": categoria.pk,
                "data": date.today().isoformat(),
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_sem_categoria_retorna_400(
        self, auth_client: APIClient
    ) -> None:
        response = auth_client.post(
            reverse("gasto-list"),
            {
                "descricao": "Sem categoria",
                "valor": "50.00",
                "data": date.today().isoformat(),
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_data_invalida_retorna_400(
        self, auth_client: APIClient, categoria: Categoria
    ) -> None:
        response = auth_client.post(
            reverse("gasto-list"),
            {
                "descricao": "Data inválida",
                "valor": "50.00",
                "categoria": categoria.pk,
                "data": "nao-e-uma-data",
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_patch_valor(self, auth_client: APIClient, gasto: Gasto) -> None:
        url = reverse("gasto-detail", args=[gasto.pk])
        response = auth_client.patch(url, {"valor": "99.99"})
        assert response.status_code == status.HTTP_200_OK
        gasto.refresh_from_db()
        assert gasto.valor == Decimal("99.99")

    def test_patch_descricao(
        self, auth_client: APIClient, gasto: Gasto
    ) -> None:
        url = reverse("gasto-detail", args=[gasto.pk])
        response = auth_client.patch(url, {"descricao": "Padaria"})
        assert response.status_code == status.HTTP_200_OK
        gasto.refresh_from_db()
        assert gasto.descricao == "Padaria"

    def test_criado_em_ignorado_no_create(
        self, auth_client: APIClient, categoria: Categoria
    ) -> None:
        # criado_em é auto_now_add — deve ser ignorado mesmo se enviado.
        response = auth_client.post(
            reverse("gasto-list"),
            {
                "descricao": "Teste",
                "valor": "10.00",
                "categoria": categoria.pk,
                "data": date.today().isoformat(),
                "criado_em": "2000-01-01T00:00:00Z",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        gasto = Gasto.objects.get(pk=response.data["id"])
        assert gasto.criado_em.year != 2000

    # --- Isolamento multi-usuário ---

    def test_list_nao_exibe_gastos_de_outro_usuario(
        self,
        auth_client: APIClient,
        gasto: Gasto,
        outro_user: User,
    ) -> None:
        outra_cat = Categoria.objects.create(
            nome="Transporte", usuario=outro_user
        )
        Gasto.objects.create(
            descricao="Uber",
            valor=Decimal("30.00"),
            categoria=outra_cat,
            usuario=outro_user,
            data=date.today(),
        )
        response = auth_client.get(reverse("gasto-list"))
        assert response.data["count"] == 1

    def test_retrieve_de_outro_usuario_retorna_404(
        self, auth_client: APIClient, outro_user: User
    ) -> None:
        outra_cat = Categoria.objects.create(
            nome="Transporte", usuario=outro_user
        )
        outro_gasto = Gasto.objects.create(
            descricao="Uber",
            valor=Decimal("30.00"),
            categoria=outra_cat,
            usuario=outro_user,
            data=date.today(),
        )
        url = reverse("gasto-detail", args=[outro_gasto.pk])
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_de_outro_usuario_retorna_404(
        self,
        auth_client: APIClient,
        outro_user: User,
        categoria: Categoria,
    ) -> None:
        outra_cat = Categoria.objects.create(
            nome="Transporte", usuario=outro_user
        )
        outro_gasto = Gasto.objects.create(
            descricao="Uber",
            valor=Decimal("30.00"),
            categoria=outra_cat,
            usuario=outro_user,
            data=date.today(),
        )
        url = reverse("gasto-detail", args=[outro_gasto.pk])
        response = auth_client.put(
            url,
            {
                "descricao": "Hackeado",
                "valor": "1.00",
                "categoria": categoria.pk,
                "data": date.today().isoformat(),
            },
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_destroy_de_outro_usuario_retorna_404(
        self, auth_client: APIClient, outro_user: User
    ) -> None:
        outra_cat = Categoria.objects.create(
            nome="Transporte", usuario=outro_user
        )
        outro_gasto = Gasto.objects.create(
            descricao="Uber",
            valor=Decimal("30.00"),
            categoria=outra_cat,
            usuario=outro_user,
            data=date.today(),
        )
        url = reverse("gasto-detail", args=[outro_gasto.pk])
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    # --- Serializer ignora campo usuario enviado pelo cliente ---

    def test_usuario_enviado_pelo_cliente_e_ignorado(
        self,
        auth_client: APIClient,
        user: User,
        outro_user: User,
        categoria: Categoria,
    ) -> None:
        response = auth_client.post(
            reverse("gasto-list"),
            {
                "descricao": "Teste",
                "valor": "10.00",
                "categoria": categoria.pk,
                "data": date.today().isoformat(),
                "usuario": outro_user.pk,
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        gasto = Gasto.objects.get(pk=response.data["id"])
        assert gasto.usuario == user
