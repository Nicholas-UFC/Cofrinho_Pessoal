import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from financas.models import Fonte

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
def outro_client(outro_user: User) -> APIClient:
    # Cliente autenticado como o segundo usuário.
    c = APIClient()
    response = c.post(
        "/api/token/",
        {"username": "outrouser", "password": "outropass123"},
    )
    token = response.data["access"]
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return c


@pytest.fixture
def fonte(user: User) -> Fonte:
    return Fonte.objects.create(nome="Salário", usuario=user)


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

    # --- Isolamento multi-usuário ---

    def test_list_nao_exibe_fontes_de_outro_usuario(
        self, auth_client: APIClient, fonte: Fonte, outro_user: User
    ) -> None:
        Fonte.objects.create(nome="Freelance", usuario=outro_user)
        response = auth_client.get(reverse("fonte-list"))
        assert len(response.data) == 1

    def test_retrieve_de_outro_usuario_retorna_404(
        self, auth_client: APIClient, outro_user: User
    ) -> None:
        outra = Fonte.objects.create(nome="Freelance", usuario=outro_user)
        url = reverse("fonte-detail", args=[outra.pk])
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_de_outro_usuario_retorna_404(
        self, auth_client: APIClient, outro_user: User
    ) -> None:
        outra = Fonte.objects.create(nome="Freelance", usuario=outro_user)
        url = reverse("fonte-detail", args=[outra.pk])
        response = auth_client.put(url, {"nome": "Hackeado"})
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_destroy_de_outro_usuario_retorna_404(
        self, auth_client: APIClient, outro_user: User
    ) -> None:
        outra = Fonte.objects.create(nome="Freelance", usuario=outro_user)
        url = reverse("fonte-detail", args=[outra.pk])
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    # --- Unique together por usuário ---

    def test_nome_igual_em_usuarios_diferentes_e_permitido_via_api(
        self,
        auth_client: APIClient,
        outro_client: APIClient,
        fonte: Fonte,
    ) -> None:
        # user já tem "Salário"; outro_user pode criar com o mesmo nome.
        response = outro_client.post(
            reverse("fonte-list"), {"nome": "Salário"}
        )
        assert response.status_code == status.HTTP_201_CREATED

    # --- Serializer ignora campo usuario enviado pelo cliente ---

    def test_usuario_enviado_pelo_cliente_e_ignorado(
        self, auth_client: APIClient, user: User, outro_user: User
    ) -> None:
        response = auth_client.post(
            reverse("fonte-list"),
            {"nome": "Nova Fonte", "usuario": outro_user.pk},
        )
        assert response.status_code == status.HTTP_201_CREATED
        f = Fonte.objects.get(nome="Nova Fonte")
        assert f.usuario == user
