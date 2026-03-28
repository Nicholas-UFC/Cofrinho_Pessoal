from datetime import date

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient

from financas.models import Categoria, Fonte, Gasto, LogAcesso, LogAuditoria

# ---------------------------------------------------------------------------
# Integração do sistema de auditoria — LogAcesso + LogAuditoria juntos
# ---------------------------------------------------------------------------
#
# O sistema de auditoria do projeto tem duas camadas independentes que devem
# funcionar em conjunto quando o usuário chama um endpoint:
#
# 1. LogAcesso (middleware): registra cada requisição HTTP com metadados como
#    endpoint, método, IP, usuário, origem e duração. É transparente para a
#    view — acontece antes e depois, sem que a view precise fazer nada.
#
# 2. LogAuditoria (signals): registra cada operação de CRUD nos models com
#    a ação realizada e os detalhes do objeto afetado. É disparado pelos
#    signals do Django ao salvar ou deletar um objeto.
#
# Esta suíte testa que as duas camadas operam juntas corretamente em cenários
# reais — uma chamada a POST /gastos/ deve gerar tanto um LogAcesso quanto um
# LogAuditoria. Também cobre edge cases importantes:
# — Bulk delete/update em queryset vazio não deve gerar logs espúrios.
# — Deletar um usuário deve preservar os logs existentes (com usuario=None),
#   garantindo que a trilha de auditoria não seja perdida junto com a conta.
# — O middleware detecta a origem correta (api, web, whatsapp) e o IP real
#   mesmo quando há um proxy reverso (via X-Forwarded-For).
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def user(db: None) -> User:
    return User.objects.create_user(
        username="testuser", password="testpass123"
    )


@pytest.fixture
def categoria(user: User) -> Categoria:
    return Categoria.objects.create(nome="Alimentacao", usuario=user)


@pytest.fixture
def fonte(user: User) -> Fonte:
    return Fonte.objects.create(nome="Salario", usuario=user)


def _autenticar(api_client: APIClient) -> None:
    response = api_client.post(
        "/api/token/",
        {"username": "testuser", "password": "testpass123"},
    )
    token = response.data["access"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")


# ---------------------------------------------------------------------------
# Integracao: endpoint gera LogAcesso + LogAuditoria simultaneamente
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_criar_gasto_gera_log_acesso_e_auditoria(
    api_client: APIClient, user: User, categoria: Categoria
) -> None:
    _autenticar(api_client)
    api_client.post(
        reverse("gasto-list"),
        {
            "descricao": "Almoco",
            "valor": "30.00",
            "categoria": categoria.pk,
            "data": str(date.today()),
        },
    )

    url = reverse("gasto-list")
    assert LogAcesso.objects.filter(endpoint=url, metodo="POST").exists()
    assert LogAuditoria.objects.filter(modelo="Gasto", acao="criado").exists()


@pytest.mark.django_db
def test_criar_entrada_gera_log_acesso_e_auditoria(
    api_client: APIClient, user: User, fonte: Fonte
) -> None:
    _autenticar(api_client)
    api_client.post(
        reverse("entrada-list"),
        {
            "descricao": "Salario",
            "valor": "3000.00",
            "fonte": fonte.pk,
            "data": str(date.today()),
        },
    )

    url = reverse("entrada-list")
    assert LogAcesso.objects.filter(endpoint=url, metodo="POST").exists()
    assert LogAuditoria.objects.filter(
        modelo="Entrada", acao="criado"
    ).exists()


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_bulk_delete_vazio_nao_gera_log(
    user: User, categoria: Categoria
) -> None:
    Gasto.objects.filter(pk=99999).delete()

    assert not LogAuditoria.objects.filter(
        modelo="Gasto", acao="bulk_deletado"
    ).exists()


@pytest.mark.django_db
def test_bulk_update_vazio_nao_gera_log(
    user: User, categoria: Categoria
) -> None:
    Gasto.objects.filter(pk=99999).update(descricao="Nao existe")

    assert not LogAuditoria.objects.filter(
        modelo="Gasto", acao="bulk_atualizado"
    ).exists()


@pytest.mark.django_db
def test_deletar_usuario_mantem_logs_com_null(db: None) -> None:
    novo_user = User.objects.create_user(
        username="temporario", password="pass123"
    )
    assert LogAuditoria.objects.filter(
        modelo="User", objeto_id=novo_user.pk
    ).exists()

    novo_user.delete()

    logs = LogAuditoria.objects.filter(modelo="User")
    assert logs.exists()
    assert all(log.usuario is None for log in logs)


# ---------------------------------------------------------------------------
# Middleware — origem API e IP via X-Forwarded-For
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_origem_api_detectada(api_client: APIClient) -> None:
    api_client.get("/api/gastos/")

    log = LogAcesso.objects.filter(endpoint="/api/gastos/").first()
    assert log is not None
    assert log.origem == "api"


@pytest.mark.django_db
def test_ip_via_x_forwarded_for(api_client: APIClient) -> None:
    api_client.get(
        "/api/gastos/",
        HTTP_X_FORWARDED_FOR="203.0.113.5, 10.0.0.1",
    )

    log = LogAcesso.objects.filter(endpoint="/api/gastos/").first()
    assert log is not None
    assert log.ip == "203.0.113.5"
