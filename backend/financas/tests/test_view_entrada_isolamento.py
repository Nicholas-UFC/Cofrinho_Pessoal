from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from financas.models import Entrada, Fonte

# ---------------------------------------------------------------------------
# Isolamento multi-usuário no endpoint de Entradas
# ---------------------------------------------------------------------------
#
# Esta suíte espelha a lógica de isolamento testada para Gastos, mas aplicada
# ao modelo Entrada.  Um usuário autenticado deve ver apenas suas próprias
# entradas financeiras — qualquer tentativa de listar, visualizar, editar ou
# excluir uma entrada de outro usuário deve receber 404.
#
# O teste final verifica que o campo `usuario` é somente-leitura do ponto de
# vista da API: mesmo que o cliente envie um ID diferente no corpo da requisição,
# o serializer descarta esse valor e vincula o registro ao usuário do token JWT.
# Isso é essencial para evitar que um cliente mal-intencionado tente associar
# uma entrada financeira a outro usuário do sistema.
# ---------------------------------------------------------------------------


@pytest.fixture
def client() -> APIClient:
    return APIClient()


@pytest.fixture
def user(db: None) -> User:
    return User.objects.create_user(
        username="testuser", password="testpass123"
    )


@pytest.fixture
def auth_client(client: APIClient, user: User) -> APIClient:
    response = client.post(
        "/api/token/",
        {"username": "testuser", "password": "testpass123"},
    )
    token = response.data["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.fixture
def outro_user(db: None) -> User:
    return User.objects.create_user(
        username="outrouser", password="outropass123"
    )


@pytest.fixture
def fonte(user: User) -> Fonte:
    return Fonte.objects.create(nome="Salário", usuario=user)


@pytest.mark.django_db
class TestEntradaIsolamento:
    def test_list_nao_exibe_entradas_de_outro_usuario(
        self,
        auth_client: APIClient,
        user: User,
        fonte: Fonte,
        outro_user: User,
    ) -> None:
        # Cria uma entrada para o usuário autenticado e outra para outro
        # usuário. A listagem deve retornar apenas a do usuário autenticado.
        Entrada.objects.create(
            descricao="Minha Entrada",
            valor=Decimal("1000.00"),
            fonte=fonte,
            usuario=user,
            data=date.today(),
        )
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

    def test_usuario_enviado_pelo_cliente_e_ignorado(
        self,
        auth_client: APIClient,
        user: User,
        outro_user: User,
        fonte: Fonte,
    ) -> None:
        # Mesmo enviando o ID de outro usuário no payload, o backend deve usar
        # o usuário autenticado via JWT.
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
