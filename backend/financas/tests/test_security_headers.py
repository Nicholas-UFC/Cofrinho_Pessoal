import pytest
from django.contrib.auth.models import User
from django.test import Client

# ---------------------------------------------------------------------------
# Cabeçalhos de segurança — OWASP práticas 140, 150, 162
#
# Verifica que todas as respostas da API contêm os cabeçalhos de segurança
# obrigatórios e que o header Server não expõe informações do servidor.
# ---------------------------------------------------------------------------


@pytest.fixture
def client() -> Client:
    return Client()


@pytest.fixture
def usuario(db: None) -> User:
    return User.objects.create_user(
        username="header_user", password="Senha@Forte12"
    )


@pytest.mark.django_db
def test_content_security_policy_presente(client: Client) -> None:
    resp = client.get("/api/financas/gastos/")
    assert "Content-Security-Policy" in resp


@pytest.mark.django_db
def test_csp_bloqueia_frame_ancestors(client: Client) -> None:
    resp = client.get("/api/financas/gastos/")
    assert "frame-ancestors 'none'" in resp["Content-Security-Policy"]


@pytest.mark.django_db
def test_referrer_policy_presente(client: Client) -> None:
    resp = client.get("/api/financas/gastos/")
    assert "Referrer-Policy" in resp
    assert resp["Referrer-Policy"] == "strict-origin-when-cross-origin"


@pytest.mark.django_db
def test_permissions_policy_presente(client: Client) -> None:
    resp = client.get("/api/financas/gastos/")
    assert "Permissions-Policy" in resp


@pytest.mark.django_db
def test_cache_control_no_store_em_api(client: Client) -> None:
    """Endpoints /api/ não devem ser cacheados — OWASP prática 140."""
    resp = client.get("/api/financas/gastos/")
    assert "Cache-Control" in resp
    assert "no-store" in resp["Cache-Control"]


@pytest.mark.django_db
def test_server_header_removido(client: Client) -> None:
    """Header Server não deve expor informações do servidor — OWASP 162."""
    resp = client.get("/api/financas/gastos/")
    assert "Server" not in resp or resp.get("Server", "") == ""


@pytest.mark.django_db
def test_x_frame_options_deny(client: Client) -> None:
    resp = client.get("/api/financas/gastos/")
    assert resp.get("X-Frame-Options") == "DENY"


@pytest.mark.django_db
def test_x_content_type_options_nosniff(client: Client) -> None:
    resp = client.get("/api/financas/gastos/")
    assert resp.get("X-Content-Type-Options") == "nosniff"
