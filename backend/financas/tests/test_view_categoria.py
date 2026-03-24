import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from financas.models import Categoria, Fonte

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
def categoria(user: User) -> Categoria:
    return Categoria.objects.create(nome="Alimentação", usuario=user)


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

    # --- Isolamento multi-usuário ---

    def test_list_nao_exibe_categorias_de_outro_usuario(
        self,
        auth_client: APIClient,
        categoria: Categoria,
        outro_user: User,
    ) -> None:
        # Categoria de outro usuário não deve aparecer na listagem.
        Categoria.objects.create(nome="Lazer", usuario=outro_user)
        response = auth_client.get(reverse("categoria-list"))
        assert len(response.data) == 1

    def test_retrieve_de_outro_usuario_retorna_404(
        self, auth_client: APIClient, outro_user: User
    ) -> None:
        outra = Categoria.objects.create(nome="Lazer", usuario=outro_user)
        url = reverse("categoria-detail", args=[outra.pk])
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_de_outro_usuario_retorna_404(
        self, auth_client: APIClient, outro_user: User
    ) -> None:
        outra = Categoria.objects.create(nome="Lazer", usuario=outro_user)
        url = reverse("categoria-detail", args=[outra.pk])
        response = auth_client.put(url, {"nome": "Hackeado"})
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_destroy_de_outro_usuario_retorna_404(
        self, auth_client: APIClient, outro_user: User
    ) -> None:
        outra = Categoria.objects.create(nome="Lazer", usuario=outro_user)
        url = reverse("categoria-detail", args=[outra.pk])
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    # --- Unique together por usuário ---

    def test_nome_igual_em_usuarios_diferentes_e_permitido_via_api(
        self,
        auth_client: APIClient,
        outro_client: APIClient,
        categoria: Categoria,
    ) -> None:
        # user já tem "Alimentação"; outro_user pode criar com o mesmo nome.
        response = outro_client.post(
            reverse("categoria-list"), {"nome": "Alimentação"}
        )
        assert response.status_code == status.HTTP_201_CREATED

    # --- Serializer ignora campo usuario enviado pelo cliente ---

    def test_usuario_enviado_pelo_cliente_e_ignorado(
        self,
        auth_client: APIClient,
        user: User,
        outro_user: User,
    ) -> None:
        # Mesmo enviando o ID de outro usuário, o servidor usa o JWT.
        response = auth_client.post(
            reverse("categoria-list"),
            {"nome": "Nova", "usuario": outro_user.pk},
        )
        assert response.status_code == status.HTTP_201_CREATED
        cat = Categoria.objects.get(nome="Nova")
        assert cat.usuario == user


# ---------------------------------------------------------------------------
# Regressão — paginação desabilitada em Categoria e Fonte
# ---------------------------------------------------------------------------
# Bug: DEFAULT_PAGINATION_CLASS global fazia CategoriaViewSet e FonteViewSet
# retornarem {count, next, previous, results:[]} em vez de lista plana.
# O frontend chamava categorias.map() e recebia
# "TypeError: categorias.map is not a function", travando /cadastro.


@pytest.mark.django_db
class TestCategoriaFonteSemPaginacao:
    def test_categorias_retorna_lista_plana(
        self, auth_client: APIClient, categoria: Categoria
    ) -> None:
        # Regressão: deve ser lista, não dict paginado {count, results}.
        response = auth_client.get(reverse("categoria-list"))
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)

    def test_fontes_retorna_lista_plana(self, auth_client: APIClient) -> None:
        # Regressão: deve ser lista, não dict paginado {count, results}.
        Fonte.objects.create(
            nome="Salário",
            usuario=User.objects.get(username="testuser"),
        )
        response = auth_client.get(reverse("fonte-list"))
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
