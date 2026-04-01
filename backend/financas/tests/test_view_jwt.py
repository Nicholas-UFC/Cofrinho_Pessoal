import time

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

# ---------------------------------------------------------------------------
# JWT — autenticação via cookies httpOnly (OWASP prática 76)
#
# Cobre token inválido, expirado, refresh via cookie e fluxo de login.
# ---------------------------------------------------------------------------


@pytest.fixture
def client() -> APIClient:
    return APIClient()


@pytest.fixture
def user(db: None) -> User:
    return User.objects.create_user(
        username="testuser", password="testpass123"
    )


@pytest.mark.django_db
class TestTokenInvalido:
    def test_token_malformado_retorna_401(
        self, client: APIClient
    ) -> None:
        client.credentials(
            HTTP_AUTHORIZATION="Bearer token_invalido_xyz"
        )
        response = client.get(reverse("gasto-list"))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_bearer_vazio_retorna_401(
        self, client: APIClient
    ) -> None:
        client.credentials(HTTP_AUTHORIZATION="Bearer ")
        response = client.get(reverse("gasto-list"))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_header_sem_bearer_retorna_401(
        self, client: APIClient, user: User
    ) -> None:
        # Token válido mas enviado sem o prefixo "Bearer"
        token = str(AccessToken.for_user(user))
        client.credentials(HTTP_AUTHORIZATION=token)
        response = client.get(reverse("gasto-list"))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestTokenExpirado:
    def test_token_expirado_retorna_401(
        self, client: APIClient, user: User
    ) -> None:
        # Cria token válido e retrocede o exp 10 segundos no passado.
        token = AccessToken.for_user(user)
        token.payload["exp"] = int(time.time()) - 10
        client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token!s}"
        )
        response = client.get(reverse("gasto-list"))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestTokenRefresh:
    def test_refresh_via_cookie_gera_novo_access(
        self, client: APIClient, user: User
    ) -> None:
        """Refresh via cookie deve retornar cookie com novo access token."""
        refresh = RefreshToken.for_user(user)
        client.cookies["refresh"] = str(refresh)
        response = client.post("/api/token/refresh/")
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.cookies

    def test_novo_cookie_access_autentica_com_sucesso(
        self, client: APIClient, user: User
    ) -> None:
        """Access token do cookie deve autenticar rotas protegidas."""
        refresh = RefreshToken.for_user(user)
        client.cookies["refresh"] = str(refresh)
        client.post("/api/token/refresh/")
        # Cookie 'access' foi definido pela resposta anterior.
        response = client.get(reverse("gasto-list"))
        assert response.status_code == status.HTTP_200_OK

    def test_refresh_invalido_retorna_401(
        self, client: APIClient
    ) -> None:
        client.cookies["refresh"] = "refresh_invalido_xyz"
        response = client.post("/api/token/refresh/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_ausente_retorna_401(
        self, client: APIClient
    ) -> None:
        """Sem cookie de refresh, deve retornar 401."""
        response = client.post("/api/token/refresh/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestFluxoLogin:
    def test_login_valido_define_cookies_e_retorna_info_usuario(
        self, client: APIClient, user: User
    ) -> None:
        """Login deve definir cookies httpOnly e retornar username/is_staff."""
        response = client.post(
            "/api/token/",
            {"username": "testuser", "password": "testpass123"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.cookies
        assert "refresh" in response.cookies
        assert response.cookies["access"]["httponly"]
        body = response.json()
        assert body["username"] == "testuser"
        assert "access" not in body
        assert "refresh" not in body

    def test_login_com_credenciais_erradas_retorna_401(
        self, client: APIClient, user: User
    ) -> None:
        response = client.post(
            "/api/token/",
            {"username": "testuser", "password": "senha_errada"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_cookie_do_login_autentica_api(
        self, client: APIClient, user: User
    ) -> None:
        """Cookie definido no login deve autenticar rotas protegidas."""
        client.post(
            "/api/token/",
            {"username": "testuser", "password": "testpass123"},
        )
        # Cookie 'access' foi definido pelo login.
        response = client.get(reverse("gasto-list"))
        assert response.status_code == status.HTTP_200_OK
