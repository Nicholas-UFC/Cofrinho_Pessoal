from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from financas.models import Categoria, Gasto

# ---------------------------------------------------------------------------
# Isolamento multi-usuário no endpoint de Gastos
# ---------------------------------------------------------------------------
#
# Esta suíte garante que um usuário autenticado nunca consiga enxergar, alterar
# ou deletar registros que pertencem a outro usuário.  A regra de negócio é
# simples: cada queryset do GastoViewSet é filtrado pelo usuário do JWT, então
# qualquer tentativa de acessar um recurso alheio deve retornar 404 — como se
# o registro simplesmente não existisse para aquele usuário.
#
# Também verificamos que o campo `usuario` no payload de criação é
# completamente ignorado pelo serializer: mesmo que o cliente envie o PK de
# outro usuário, o backend usa o usuário autenticado via token, impedindo
# escalação de privilégio.
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
def categoria(user: User) -> Categoria:
    return Categoria.objects.create(nome="Alimentação", usuario=user)


@pytest.mark.django_db
class TestGastoIsolamento:
    def test_list_nao_exibe_gastos_de_outro_usuario(
        self,
        auth_client: APIClient,
        user: User,
        outro_user: User,
        categoria: Categoria,
    ) -> None:
        # Cria um gasto do próprio usuário e um de outro usuário.
        # A listagem deve retornar apenas o do usuário autenticado.
        Gasto.objects.create(
            descricao="Meu Gasto",
            valor=Decimal("50.00"),
            categoria=categoria,
            usuario=user,
            data=date.today(),
        )
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

    def test_usuario_enviado_pelo_cliente_e_ignorado(
        self,
        auth_client: APIClient,
        user: User,
        outro_user: User,
        categoria: Categoria,
    ) -> None:
        # Mesmo enviando o ID de outro usuário no payload, o backend deve usar
        # o usuário autenticado via JWT — impedindo qualquer tentativa de
        # criar registros em nome de outra pessoa.
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
