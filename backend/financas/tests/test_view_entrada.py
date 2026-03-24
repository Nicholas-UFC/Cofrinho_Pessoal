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
def fonte(user: User) -> Fonte:
    return Fonte.objects.create(nome="Salário", usuario=user)


@pytest.fixture
def entrada(user: User, fonte: Fonte) -> Entrada:
    return Entrada.objects.create(
        descricao="Salário Janeiro",
        valor=Decimal("3000.00"),
        fonte=fonte,
        usuario=user,
        data=date.today(),
    )


# ---------------------------------------------------------------------------
# Entrada
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestEntradaViewSet:
    def test_list(self, auth_client: APIClient, entrada: Entrada) -> None:
        response = auth_client.get(reverse("entrada-list"))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

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

    def test_create_valor_zero_retorna_400(
        self, auth_client: APIClient, fonte: Fonte
    ) -> None:
        response = auth_client.post(
            reverse("entrada-list"),
            {
                "descricao": "Inválido",
                "valor": "0.00",
                "fonte": fonte.pk,
                "data": date.today().isoformat(),
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_sem_descricao_retorna_400(
        self, auth_client: APIClient, fonte: Fonte
    ) -> None:
        response = auth_client.post(
            reverse("entrada-list"),
            {
                "valor": "500.00",
                "fonte": fonte.pk,
                "data": date.today().isoformat(),
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_sem_fonte_retorna_400(
        self, auth_client: APIClient
    ) -> None:
        response = auth_client.post(
            reverse("entrada-list"),
            {
                "descricao": "Sem fonte",
                "valor": "500.00",
                "data": date.today().isoformat(),
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_data_invalida_retorna_400(
        self, auth_client: APIClient, fonte: Fonte
    ) -> None:
        response = auth_client.post(
            reverse("entrada-list"),
            {
                "descricao": "Data inválida",
                "valor": "500.00",
                "fonte": fonte.pk,
                "data": "nao-e-uma-data",
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_patch_valor(
        self, auth_client: APIClient, entrada: Entrada
    ) -> None:
        url = reverse("entrada-detail", args=[entrada.pk])
        response = auth_client.patch(url, {"valor": "3500.00"})
        assert response.status_code == status.HTTP_200_OK
        entrada.refresh_from_db()
        assert entrada.valor == Decimal("3500.00")

    def test_patch_descricao(
        self, auth_client: APIClient, entrada: Entrada
    ) -> None:
        url = reverse("entrada-detail", args=[entrada.pk])
        response = auth_client.patch(url, {"descricao": "Salário Março"})
        assert response.status_code == status.HTTP_200_OK
        entrada.refresh_from_db()
        assert entrada.descricao == "Salário Março"

    def test_criado_em_ignorado_no_create(
        self, auth_client: APIClient, fonte: Fonte
    ) -> None:
        # criado_em é auto_now_add — deve ser ignorado mesmo se enviado.
        response = auth_client.post(
            reverse("entrada-list"),
            {
                "descricao": "Teste",
                "valor": "100.00",
                "fonte": fonte.pk,
                "data": date.today().isoformat(),
                "criado_em": "2000-01-01T00:00:00Z",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        entrada = Entrada.objects.get(pk=response.data["id"])
        assert entrada.criado_em.year != 2000

    # --- Isolamento multi-usuário ---

    def test_list_nao_exibe_entradas_de_outro_usuario(
        self,
        auth_client: APIClient,
        entrada: Entrada,
        outro_user: User,
    ) -> None:
        outra_fonte = Fonte.objects.create(
            nome="Freelance", usuario=outro_user
        )
        Entrada.objects.create(
            descricao="Renda extra",
            valor=Decimal("500.00"),
            fonte=outra_fonte,
            usuario=outro_user,
            data=date.today(),
        )
        response = auth_client.get(reverse("entrada-list"))
        assert response.data["count"] == 1

    def test_retrieve_de_outro_usuario_retorna_404(
        self, auth_client: APIClient, outro_user: User
    ) -> None:
        outra_fonte = Fonte.objects.create(
            nome="Freelance", usuario=outro_user
        )
        outra_entrada = Entrada.objects.create(
            descricao="Renda extra",
            valor=Decimal("500.00"),
            fonte=outra_fonte,
            usuario=outro_user,
            data=date.today(),
        )
        url = reverse("entrada-detail", args=[outra_entrada.pk])
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_de_outro_usuario_retorna_404(
        self, auth_client: APIClient, outro_user: User, fonte: Fonte
    ) -> None:
        outra_fonte = Fonte.objects.create(
            nome="Freelance", usuario=outro_user
        )
        outra_entrada = Entrada.objects.create(
            descricao="Renda extra",
            valor=Decimal("500.00"),
            fonte=outra_fonte,
            usuario=outro_user,
            data=date.today(),
        )
        url = reverse("entrada-detail", args=[outra_entrada.pk])
        response = auth_client.put(
            url,
            {
                "descricao": "Hackeado",
                "valor": "1.00",
                "fonte": fonte.pk,
                "data": date.today().isoformat(),
            },
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_destroy_de_outro_usuario_retorna_404(
        self, auth_client: APIClient, outro_user: User
    ) -> None:
        outra_fonte = Fonte.objects.create(
            nome="Freelance", usuario=outro_user
        )
        outra_entrada = Entrada.objects.create(
            descricao="Renda extra",
            valor=Decimal("500.00"),
            fonte=outra_fonte,
            usuario=outro_user,
            data=date.today(),
        )
        url = reverse("entrada-detail", args=[outra_entrada.pk])
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    # --- Serializer ignora campo usuario enviado pelo cliente ---

    def test_usuario_enviado_pelo_cliente_e_ignorado(
        self,
        auth_client: APIClient,
        user: User,
        outro_user: User,
        fonte: Fonte,
    ) -> None:
        response = auth_client.post(
            reverse("entrada-list"),
            {
                "descricao": "Teste",
                "valor": "100.00",
                "fonte": fonte.pk,
                "data": date.today().isoformat(),
                "usuario": outro_user.pk,
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        entrada = Entrada.objects.get(pk=response.data["id"])
        assert entrada.usuario == user


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
