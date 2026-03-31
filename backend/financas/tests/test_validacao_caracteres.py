import pytest
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

# ---------------------------------------------------------------------------
# Validação de caracteres perigosos nos campos de texto — OWASP 14-16
#
# Verifica que null bytes, quebras de linha e path traversal são rejeitados
# nos campos `nome` (Categoria/Fonte) e `descricao` (Gasto/Entrada).
# ---------------------------------------------------------------------------


@pytest.fixture
def usuario(db: None) -> User:
    return User.objects.create_user(
        username="char_user", password="Senha@Forte12"
    )


@pytest.fixture
def client(usuario: User) -> APIClient:
    api = APIClient()
    token = AccessToken.for_user(usuario)
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return api


@pytest.fixture
def categoria(usuario: User, client: APIClient) -> int:
    resp = client.post(
        "/api/financas/categorias/", {"nome": "Alimentacao"}
    )
    return resp.data["id"]


@pytest.fixture
def fonte(usuario: User, client: APIClient) -> int:
    resp = client.post(
        "/api/financas/fontes/", {"nome": "Salario"}
    )
    return resp.data["id"]


_ENTRADAS_PERIGOSAS = [
    ("null byte", "nome\x00invalido"),
    ("newline", "nome\ninvalido"),
    ("carriage return", "nome\rinvalido"),
    ("path traversal", "../../../etc/passwd"),
    ("path traversal windows", "..\\..\\windows"),
]


@pytest.mark.django_db
@pytest.mark.parametrize("descricao,valor", _ENTRADAS_PERIGOSAS)
def test_categoria_rejeita_nome_perigoso(
    client: APIClient, descricao: str, valor: str
) -> None:
    resp = client.post("/api/financas/categorias/", {"nome": valor})
    assert resp.status_code == status.HTTP_400_BAD_REQUEST, (
        f"Deveria rejeitar '{descricao}' no nome de categoria"
    )


@pytest.mark.django_db
@pytest.mark.parametrize("descricao,valor", _ENTRADAS_PERIGOSAS)
def test_fonte_rejeita_nome_perigoso(
    client: APIClient, descricao: str, valor: str
) -> None:
    resp = client.post("/api/financas/fontes/", {"nome": valor})
    assert resp.status_code == status.HTTP_400_BAD_REQUEST, (
        f"Deveria rejeitar '{descricao}' no nome de fonte"
    )


@pytest.mark.django_db
@pytest.mark.parametrize("descricao,valor", _ENTRADAS_PERIGOSAS)
def test_gasto_rejeita_descricao_perigosa(
    client: APIClient, categoria: int, descricao: str, valor: str
) -> None:
    from datetime import date  # noqa: PLC0415

    resp = client.post(
        "/api/financas/gastos/",
        {
            "descricao": valor,
            "valor": "10.00",
            "categoria": categoria,
            "data": str(date.today()),
        },
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST, (
        f"Deveria rejeitar '{descricao}' na descricao de gasto"
    )


@pytest.mark.django_db
@pytest.mark.parametrize("descricao,valor", _ENTRADAS_PERIGOSAS)
def test_entrada_rejeita_descricao_perigosa(
    client: APIClient, fonte: int, descricao: str, valor: str
) -> None:
    from datetime import date  # noqa: PLC0415

    resp = client.post(
        "/api/financas/entradas/",
        {
            "descricao": valor,
            "valor": "10.00",
            "fonte": fonte,
            "data": str(date.today()),
        },
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST, (
        f"Deveria rejeitar '{descricao}' na descricao de entrada"
    )


@pytest.mark.django_db
def test_nome_seguro_aceito_em_categoria(client: APIClient) -> None:
    resp = client.post(
        "/api/financas/categorias/", {"nome": "Alimentação Normal"}
    )
    assert resp.status_code == status.HTTP_201_CREATED
