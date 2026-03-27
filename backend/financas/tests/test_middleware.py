import pytest
from django.contrib.auth.models import User
from django.test import Client

from financas.models import LogAcesso

# ---------------------------------------------------------------------------
# Middleware de LogAcesso — registro automático de requisições
# ---------------------------------------------------------------------------
#
# O LogAcessoMiddleware intercepta todas as requisições ao servidor e salva
# um registro no banco com os metadados da chamada. Os testes aqui verificam
# cada campo que o middleware é responsável por preencher:
#
# — `usuario`: None para requisições anônimas, o objeto User para autenticadas.
# — `metodo`: o verbo HTTP (GET, POST, etc.).
# — `origem`: "web" quando vem do frontend (detectado pelo Referer),
#   "whatsapp" para o endpoint `/api/whatsapp/webhook/`,
#   "api" para chamadas diretas sem Referer.
# — `dispositivo`: "mobile" ou "desktop", detectado pelo User-Agent.
# — `status_code`: o código de resposta HTTP retornado pela view.
# — `duracao_ms`: tempo de processamento da requisição em milissegundos.
# — Requisições ao `/admin/` não geram LogAcesso — são excluídas pelo
#   middleware para evitar poluir os logs com acessos administrativos.
# ---------------------------------------------------------------------------


@pytest.fixture
def user(db: None) -> User:
    return User.objects.create_user(username="testuser", password="pass123")


@pytest.fixture
def cliente_autenticado(user: User) -> Client:
    client = Client()
    client.force_login(user)
    return client


@pytest.mark.django_db
def test_requisicao_anonima_gera_log(client: Client) -> None:

    client.get("/api/gastos/")

    log = LogAcesso.objects.filter(endpoint="/api/gastos/").first()
    assert log is not None
    assert log.usuario is None
    assert log.metodo == "GET"


@pytest.mark.django_db
def test_requisicao_autenticada_registra_usuario(
    cliente_autenticado: Client, user: User
) -> None:

    cliente_autenticado.get("/api/gastos/")

    log = LogAcesso.objects.filter(endpoint="/api/gastos/").first()
    assert log is not None
    assert log.usuario == user


@pytest.mark.django_db
def test_origem_web_detectada(client: Client) -> None:

    client.get("/api/gastos/", HTTP_REFERER="http://localhost:5173")

    log = LogAcesso.objects.filter(endpoint="/api/gastos/").first()
    assert log is not None
    assert log.origem == "web"


@pytest.mark.django_db
def test_origem_whatsapp_detectada(client: Client) -> None:

    client.post(
        "/api/whatsapp/webhook/", data={}, content_type="application/json"
    )

    log = LogAcesso.objects.filter(endpoint="/api/whatsapp/webhook/").first()
    assert log is not None
    assert log.origem == "whatsapp"


@pytest.mark.django_db
def test_dispositivo_mobile_detectado(client: Client) -> None:

    client.get(
        "/api/gastos/",
        HTTP_USER_AGENT="Mozilla/5.0 (Android 12; Mobile) AppleWebKit/537.36",
    )

    log = LogAcesso.objects.filter(endpoint="/api/gastos/").first()
    assert log is not None
    assert log.dispositivo == "mobile"


@pytest.mark.django_db
def test_dispositivo_desktop_detectado(client: Client) -> None:

    client.get(
        "/api/gastos/",
        HTTP_USER_AGENT="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    )

    log = LogAcesso.objects.filter(endpoint="/api/gastos/").first()
    assert log is not None
    assert log.dispositivo == "desktop"


@pytest.mark.django_db
def test_admin_nao_gera_log(client: Client) -> None:

    client.get("/admin/")

    assert not LogAcesso.objects.filter(endpoint="/admin/").exists()


@pytest.mark.django_db
def test_status_code_registrado(client: Client) -> None:

    client.get("/api/gastos/")

    log = LogAcesso.objects.filter(endpoint="/api/gastos/").first()
    assert log is not None
    assert log.status_code > 0


@pytest.mark.django_db
def test_duracao_registrada(client: Client) -> None:

    client.get("/api/gastos/")

    log = LogAcesso.objects.filter(endpoint="/api/gastos/").first()
    assert log is not None
    assert log.duracao_ms >= 0
