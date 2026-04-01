from rest_framework_simplejwt.tokens import RefreshToken
import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from financas.models import Categoria, Fonte

# ---------------------------------------------------------------------------
# CRUD, isolamento e unicidade no endpoint de Categorias
# ---------------------------------------------------------------------------
#
# Categorias são entidades de configuração: o usuário as cria uma vez e as
# reutiliza em todos os gastos. Por isso, o endpoint de Categorias tem regras
# ligeiramente diferentes dos endpoints de Gasto e Entrada:
#
# — A listagem retorna uma lista plana (sem paginação), pois o frontend precisa
#   renderizar todas as categorias num <select> de uma só vez.
# — Nomes duplicados para o mesmo usuário são proibidos (unique_together).
#   Mas o mesmo nome pode existir para usuários diferentes — é uma restrição
#   por usuário, não global.
# — Isolamento multi-usuário: cada usuário vê apenas suas próprias categorias.
#   Tentar acessar, editar ou excluir uma categoria de outro usuário retorna
#   404.
# — O campo `usuario` é somente-leitura: mesmo que o cliente envie outro
#   ID, o backend vincula a categoria ao usuário autenticado via JWT.
#
# O teste de regressão de paginação (lista plana vs. dict paginado) foi movido
# para `test_view_paginacao.py`, onde ficam concentrados os testes de estrutura
# de resposta paginada e não-paginada.
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
def outro_client(outro_user: User) -> APIClient:
    # Cliente autenticado como o segundo usuário.
    c = APIClient()
    token = RefreshToken.for_user(outro_user)
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
    return c


@pytest.fixture
def categoria(user: User) -> Categoria:
    return Categoria.objects.create(nome="Alimentação", usuario=user)


@pytest.fixture
def fonte(user: User) -> Fonte:
    return Fonte.objects.create(nome="Salário", usuario=user)


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
