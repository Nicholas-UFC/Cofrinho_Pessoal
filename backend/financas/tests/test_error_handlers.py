import pytest
from django.test import Client

# ---------------------------------------------------------------------------
# Handlers de erro genéricos — OWASP práticas 107-109
#
# Verifica que 404 retorna JSON genérico sem expor detalhes internos,
# e que a resposta não vaza stack traces, nomes de views ou paths internos.
# ---------------------------------------------------------------------------


@pytest.fixture
def client() -> Client:
    return Client()


@pytest.mark.django_db
def test_rota_inexistente_retorna_404(client: Client) -> None:
    resp = client.get("/api/rota-que-nao-existe-12345/")
    assert resp.status_code == 404


@pytest.mark.django_db
def test_404_retorna_json(client: Client) -> None:
    resp = client.get("/api/rota-inexistente/")
    assert resp["Content-Type"].startswith("application/json")


@pytest.mark.django_db
def test_404_nao_vaza_stack_trace(client: Client) -> None:
    resp = client.get("/api/rota-inexistente/")
    corpo = resp.json()
    assert "traceback" not in str(corpo).lower()
    assert "exception" not in str(corpo).lower()
    assert "debug" not in str(corpo).lower()


@pytest.mark.django_db
def test_404_mensagem_generica(client: Client) -> None:
    resp = client.get("/api/rota-inexistente/")
    corpo = resp.json()
    assert "erro" in corpo


@pytest.mark.django_db
def test_404_nao_expoe_caminho_interno(client: Client) -> None:
    resp = client.get("/api/rota-inexistente/")
    corpo = str(resp.json())
    assert "site-packages" not in corpo
    assert "backend\\" not in corpo
    assert "config\\" not in corpo
