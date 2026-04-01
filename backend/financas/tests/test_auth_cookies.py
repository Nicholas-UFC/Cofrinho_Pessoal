import pytest
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

# ---------------------------------------------------------------------------
# Autenticação via cookies httpOnly — OWASP prática 76
#
# "Set cookies with the HttpOnly attribute."
# Verifica que login define cookies, que as rotas protegidas aceitam cookie,
# e que o logout limpa os cookies e blacklista o refresh token.
# ---------------------------------------------------------------------------


@pytest.fixture
def usuario(db: None) -> User:
    return User.objects.create_user(
        username="cookie_user", password="Senha@Forte12"
    )


@pytest.fixture
def client() -> APIClient:
    return APIClient()


@pytest.mark.django_db
def test_login_define_cookies_httponly(
    client: APIClient, usuario: User
) -> None:
    """Login deve retornar cookies httpOnly com access e refresh."""
    resp = client.post(
        "/api/token/",
        {"username": "cookie_user", "password": "Senha@Forte12"},
        content_type="application/json",
    )
    assert resp.status_code == status.HTTP_200_OK
    assert "access" in resp.cookies
    assert "refresh" in resp.cookies
    assert resp.cookies["access"]["httponly"]
    assert resp.cookies["refresh"]["httponly"]


@pytest.mark.django_db
def test_login_retorna_username_e_is_staff(
    client: APIClient, usuario: User
) -> None:
    """Login deve retornar username e is_staff no corpo, não os tokens."""
    resp = client.post(
        "/api/token/",
        {"username": "cookie_user", "password": "Senha@Forte12"},
        content_type="application/json",
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["username"] == "cookie_user"
    assert "access" not in resp.json()
    assert "refresh" not in resp.json()


@pytest.mark.django_db
def test_rota_protegida_aceita_cookie(
    client: APIClient, usuario: User
) -> None:
    """Rotas protegidas devem aceitar autenticação via cookie."""
    refresh = RefreshToken.for_user(usuario)
    client.cookies["access"] = str(refresh.access_token)

    resp = client.get("/api/me/")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["username"] == "cookie_user"


@pytest.mark.django_db
def test_rota_protegida_sem_cookie_retorna_401(client: APIClient) -> None:
    """Sem cookie, rotas protegidas devem retornar 401."""
    resp = client.get("/api/me/")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_refresh_via_cookie_retorna_novo_cookie(
    client: APIClient, usuario: User
) -> None:
    """Refresh via cookie deve retornar novo cookie de access."""
    refresh = RefreshToken.for_user(usuario)
    client.cookies["refresh"] = str(refresh)

    resp = client.post("/api/token/refresh/")
    assert resp.status_code == status.HTTP_200_OK
    assert "access" in resp.cookies


@pytest.mark.django_db
def test_logout_limpa_cookies(client: APIClient, usuario: User) -> None:
    """Logout deve limpar os cookies de access e refresh."""
    refresh = RefreshToken.for_user(usuario)
    client.cookies["access"] = str(refresh.access_token)
    client.cookies["refresh"] = str(refresh)

    resp = client.post("/api/token/logout/")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.cookies["access"].value == ""
    assert resp.cookies["refresh"].value == ""
