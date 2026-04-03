from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from financas.models import Categoria, Entrada, Fonte, Gasto

# ---------------------------------------------------------------------------
# Idempotência
#
# Garante que operações seguras (PUT/PATCH/DELETE) podem ser repetidas sem
# efeitos colaterais inesperados. Comportamentos esperados:
#   - DELETE duas vezes: primeiro 204, segundo 404
#   - PUT/PATCH duas vezes com mesmo payload: ambos 200 e resultado idêntico
# ---------------------------------------------------------------------------


@pytest.fixture
def user(db: None) -> User:
    return User.objects.create_user(
        username="testuser", password="testpass123"
    )


@pytest.fixture
def auth_client(user: User) -> APIClient:
    c = APIClient()
    token = RefreshToken.for_user(user)
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
    return c


@pytest.fixture
def categoria(user: User) -> Categoria:
    return Categoria.objects.create(nome="Alimentacao", usuario=user)


@pytest.fixture
def fonte(user: User) -> Fonte:
    return Fonte.objects.create(nome="Salario", usuario=user)


@pytest.fixture
def gasto(user: User, categoria: Categoria) -> Gasto:
    return Gasto.objects.create(
        descricao="Mercado",
        valor=Decimal("100.00"),
        categoria=categoria,
        usuario=user,
        data=date.today(),
    )


@pytest.fixture
def entrada(user: User, fonte: Fonte) -> Entrada:
    return Entrada.objects.create(
        descricao="Salario",
        valor=Decimal("3000.00"),
        fonte=fonte,
        usuario=user,
        data=date.today(),
    )


# ---------------------------------------------------------------------------
# DELETE idempotente
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestDeleteIdempotente:
    def test_delete_gasto_duas_vezes_segundo_retorna_404(
        self, auth_client: APIClient, gasto: Gasto
    ) -> None:
        url = reverse("gasto-detail", args=[gasto.pk])
        primeiro = auth_client.delete(url)
        segundo = auth_client.delete(url)
        assert primeiro.status_code == status.HTTP_204_NO_CONTENT
        assert segundo.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_entrada_duas_vezes_segundo_retorna_404(
        self, auth_client: APIClient, entrada: Entrada
    ) -> None:
        url = reverse("entrada-detail", args=[entrada.pk])
        primeiro = auth_client.delete(url)
        segundo = auth_client.delete(url)
        assert primeiro.status_code == status.HTTP_204_NO_CONTENT
        assert segundo.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_categoria_sem_gastos_duas_vezes_segundo_retorna_404(
        self, auth_client: APIClient, categoria: Categoria
    ) -> None:
        # Categoria sem gastos vinculados pode ser deletada.
        url = reverse("categoria-detail", args=[categoria.pk])
        primeiro = auth_client.delete(url)
        segundo = auth_client.delete(url)
        assert primeiro.status_code == status.HTTP_204_NO_CONTENT
        assert segundo.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_fonte_sem_entradas_duas_vezes_segundo_retorna_404(
        self, auth_client: APIClient, fonte: Fonte
    ) -> None:
        url = reverse("fonte-detail", args=[fonte.pk])
        primeiro = auth_client.delete(url)
        segundo = auth_client.delete(url)
        assert primeiro.status_code == status.HTTP_204_NO_CONTENT
        assert segundo.status_code == status.HTTP_404_NOT_FOUND


# ---------------------------------------------------------------------------
# PUT idempotente
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestPutIdempotente:
    def test_put_gasto_mesmo_payload_resultado_identico(
        self,
        auth_client: APIClient,
        gasto: Gasto,
        categoria: Categoria,
    ) -> None:
        url = reverse("gasto-detail", args=[gasto.pk])
        payload = {
            "descricao": "Mercado Atualizado",
            "valor": "150.00",
            "categoria": categoria.pk,
            "data": str(date.today()),
        }
        primeiro = auth_client.put(url, payload)
        segundo = auth_client.put(url, payload)
        assert primeiro.status_code == status.HTTP_200_OK
        assert segundo.status_code == status.HTTP_200_OK
        assert primeiro.data["descricao"] == segundo.data["descricao"]
        assert primeiro.data["valor"] == segundo.data["valor"]

    def test_put_entrada_mesmo_payload_resultado_identico(
        self,
        auth_client: APIClient,
        entrada: Entrada,
        fonte: Fonte,
    ) -> None:
        url = reverse("entrada-detail", args=[entrada.pk])
        payload = {
            "descricao": "Salario Atualizado",
            "valor": "3500.00",
            "fonte": fonte.pk,
            "data": str(date.today()),
        }
        primeiro = auth_client.put(url, payload)
        segundo = auth_client.put(url, payload)
        assert primeiro.status_code == status.HTTP_200_OK
        assert segundo.status_code == status.HTTP_200_OK
        assert primeiro.data["descricao"] == segundo.data["descricao"]
        assert primeiro.data["valor"] == segundo.data["valor"]


# ---------------------------------------------------------------------------
# PATCH idempotente
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestPatchIdempotente:
    def test_patch_gasto_mesmo_valor_resultado_identico(
        self, auth_client: APIClient, gasto: Gasto
    ) -> None:
        url = reverse("gasto-detail", args=[gasto.pk])
        payload = {"valor": "200.00"}
        primeiro = auth_client.patch(url, payload)
        segundo = auth_client.patch(url, payload)
        assert primeiro.status_code == status.HTTP_200_OK
        assert segundo.status_code == status.HTTP_200_OK
        assert primeiro.data["valor"] == segundo.data["valor"]

    def test_patch_entrada_mesmo_valor_resultado_identico(
        self, auth_client: APIClient, entrada: Entrada
    ) -> None:
        url = reverse("entrada-detail", args=[entrada.pk])
        payload = {"valor": "4000.00"}
        primeiro = auth_client.patch(url, payload)
        segundo = auth_client.patch(url, payload)
        assert primeiro.status_code == status.HTTP_200_OK
        assert segundo.status_code == status.HTTP_200_OK
        assert primeiro.data["valor"] == segundo.data["valor"]
