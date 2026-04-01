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
# CRUD e validações de campo no endpoint de Entradas
# ---------------------------------------------------------------------------
#
# Esta suíte testa as operações básicas do EntradaViewSet (list, create,
# retrieve, update, patch e destroy) e as regras de validação de campo.
#
# As entradas financeiras seguem as mesmas regras de negócio dos gastos:
# valor deve ser positivo, descrição e fonte são obrigatórias, e a data
# deve estar no formato ISO 8601. O campo `criado_em` é auto_now_add e deve
# ser ignorado mesmo se enviado pelo cliente no payload de criação.
#
# Testes de isolamento multi-usuário (garantia de que um usuário não enxerga
# entradas de outro) estão em `test_view_entrada_isolamento.py`.
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

