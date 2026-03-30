import time

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

# ---------------------------------------------------------------------------
# JWT — autenticação avançada
#
# Cobre os casos que test_view_autenticacao.py não cobre: token inválido,
# token expirado, token refresh e fluxo completo de login.
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
    def test_refresh_valido_gera_novo_access_token(
        self, client: APIClient, user: User
    ) -> None:
        refresh = RefreshToken.for_user(user)
        response = client.post(
            "/api/token/refresh/", {"refresh": str(refresh)}
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data

    def test_novo_access_token_autentica_com_sucesso(
        self, client: APIClient, user: User
    ) -> None:
        refresh = RefreshToken.for_user(user)
        response = client.post(
            "/api/token/refresh/", {"refresh": str(refresh)}
        )
        novo_token = response.data["access"]
        client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {novo_token}"
        )
        response = client.get(reverse("gasto-list"))
        assert response.status_code == status.HTTP_200_OK

    def test_refresh_invalido_retorna_401(
        self, client: APIClient
    ) -> None:
        response = client.post(
            "/api/token/refresh/",
            {"refresh": "refresh_invalido_xyz"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_ausente_retorna_400(
        self, client: APIClient
    ) -> None:
        response = client.post("/api/token/refresh/", {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestFluxoLogin:
    def test_login_valido_retorna_access_e_refresh(
        self, client: APIClient, user: User
    ) -> None:
        response = client.post(
            "/api/token/",
            {"username": "testuser", "password": "testpass123"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

    def test_login_com_credenciais_erradas_retorna_401(
        self, client: APIClient, user: User
    ) -> None:
        response = client.post(
            "/api/token/",
            {"username": "testuser", "password": "senha_errada"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_access_token_do_login_autentica_api(
        self, client: APIClient, user: User
    ) -> None:
        response = client.post(
            "/api/token/",
            {"username": "testuser", "password": "testpass123"},
        )
        token = response.data["access"]
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = client.get(reverse("gasto-list"))
        assert response.status_code == status.HTTP_200_OK
