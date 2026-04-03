from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from financas.models import Categoria, Gasto

# ---------------------------------------------------------------------------
# CRUD e validações de campo no endpoint de Gastos
# ---------------------------------------------------------------------------
#
# Esta suíte testa as operações básicas do GastoViewSet (list, create,
# retrieve, update, patch e destroy) e as validações de campo que o
# serializer e o model impõem ao receber dados do cliente.
#
# Por que essas validações importam?
# — Valor negativo ou zero deve ser rejeitado com 400: o model usa um
#   validator e um CheckConstraint no banco, mas o serializer precisa
#   rejeitá-los antes mesmo de tentar salvar, devolvendo erro claro.
# — Descrição e categoria são obrigatórias; data deve estar em ISO 8601.
#   Qualquer campo faltante ou inválido deve resultar em 400, não 500.
# — O campo `criado_em` é `auto_now_add` e, por isso, somente leitura: qualquer
#   valor enviado pelo cliente nesse campo deve ser silenciosamente ignorado —
#   o servidor sempre usa o timestamp gerado pelo banco.
# — Testes de isolamento multi-usuário e de segurança do campo `usuario` estão
#   em `test_view_gasto_isolamento.py`.
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
