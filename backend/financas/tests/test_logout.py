import pytest
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

# ---------------------------------------------------------------------------
# Logout com blacklist de refresh token — OWASP prática 62
#
# "Logout functionality should fully terminate the associated session."
# Verifica que após o logout, o refresh token não pode mais ser usado.
# ---------------------------------------------------------------------------


@pytest.fixture
def usuario(db: None) -> User:
    return User.objects.create_user(
        username="logout_user", password="Senha@Forte12"
    )


@pytest.fixture
def client() -> APIClient:
    return APIClient()


@pytest.mark.django_db
def test_logout_invalida_refresh_token(
    client: APIClient, usuario: User
) -> None:
    """Após logout, o refresh token deve ser rejeitado."""
    refresh = RefreshToken.for_user(usuario)
    access = str(refresh.access_token)

    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    resp = client.post(
        "/api/token/logout/",
        {"refresh": str(refresh)},
        content_type="application/json",
    )
    assert resp.status_code == status.HTTP_200_OK

    # Tentar usar o mesmo refresh token deve falhar.
    resp_refresh = client.post(
        "/api/token/refresh/", {"refresh": str(refresh)}
    )
    assert resp_refresh.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_logout_sem_autenticacao_retorna_401(client: APIClient) -> None:
    resp = client.post(
        "/api/token/logout/",
        {"refresh": "qualquer_token"},
        content_type="application/json",
    )
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_logout_sem_refresh_retorna_400(
    client: APIClient, usuario: User
) -> None:
    access = str(AccessToken.for_user(usuario))
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    resp = client.post(
        "/api/token/logout/", {}, content_type="application/json"
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_logout_com_refresh_invalido_ainda_limpa_cookies(
    client: APIClient, usuario: User
) -> None:
    """Token inválido não deve impedir o logout — cookies devem ser limpos."""
    access = str(AccessToken.for_user(usuario))
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    resp = client.post(
        "/api/token/logout/",
        {"refresh": "token_invalido_xyz"},
        content_type="application/json",
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.cookies["access"].value == ""
    assert resp.cookies["refresh"].value == ""


@pytest.mark.django_db
def test_logout_bem_sucedido_retorna_200(
    client: APIClient, usuario: User
) -> None:
    refresh = RefreshToken.for_user(usuario)
    access = str(refresh.access_token)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    resp = client.post(
        "/api/token/logout/",
        {"refresh": str(refresh)},
        content_type="application/json",
    )
    assert resp.status_code == status.HTTP_200_OK
    assert "status" in resp.json()


@pytest.mark.django_db
def test_logout_aceita_json(client: APIClient, usuario: User) -> None:
    """Logout deve aceitar refresh token via JSON body."""
    refresh = RefreshToken.for_user(usuario)
    access = str(refresh.access_token)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    resp = client.post(
        "/api/token/logout/",
        data=f'{{"refresh": "{refresh}"}}',
        content_type="application/json",
    )
    assert resp.status_code == status.HTTP_200_OK
