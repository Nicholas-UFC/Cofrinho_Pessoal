import pytest
from django.contrib.auth.models import User

from financas.models import LogAuditoria
from whatsapp.models import SessaoConversa


@pytest.fixture
def user(db: None) -> User:
    return User.objects.create_user(username="testuser", password="pass123")


# ---------------------------------------------------------------------------
# Criação, atualização e deleção individual
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_criacao_sessao_gera_log(db: None) -> None:
    sessao = SessaoConversa.objects.create(chat_id="123@g.us")

    log = LogAuditoria.objects.get(
        modelo="SessaoConversa", objeto_id=sessao.pk
    )
    assert log.acao == "criado"


@pytest.mark.django_db
def test_atualizacao_sessao_gera_log(db: None) -> None:
    sessao = SessaoConversa.objects.create(chat_id="123@g.us")
    sessao.estado = "aguardando_valor_gasto"
    sessao.save()

    log = LogAuditoria.objects.filter(
        modelo="SessaoConversa",
        objeto_id=sessao.pk,
        acao="atualizado",
    ).first()
    assert log is not None
    assert log.detalhes["estado"] == "aguardando_valor_gasto"


@pytest.mark.django_db
def test_delecao_sessao_gera_log(db: None) -> None:
    sessao = SessaoConversa.objects.create(chat_id="123@g.us")
    sessao_id = sessao.pk
    sessao.delete()

    log = LogAuditoria.objects.get(
        modelo="SessaoConversa", objeto_id=sessao_id, acao="deletado"
    )
    assert log.acao == "deletado"


# ---------------------------------------------------------------------------
# Operações em massa
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_bulk_delete_sessao_gera_log(db: None) -> None:
    SessaoConversa.objects.create(chat_id="111@g.us")
    SessaoConversa.objects.create(chat_id="222@g.us")

    SessaoConversa.objects.all().delete()

    logs = LogAuditoria.objects.filter(
        modelo="SessaoConversa", acao="bulk_deletado"
    )
    assert logs.count() == 2


@pytest.mark.django_db
def test_bulk_update_sessao_gera_log(db: None) -> None:
    sessao = SessaoConversa.objects.create(chat_id="123@g.us")

    SessaoConversa.objects.filter(pk=sessao.pk).update(
        estado="aguardando_valor_gasto"
    )

    log = LogAuditoria.objects.get(
        modelo="SessaoConversa", acao="bulk_atualizado"
    )
    assert log.detalhes["campos"]["estado"] == "aguardando_valor_gasto"


# ---------------------------------------------------------------------------
# Log armazena detalhes da sessão
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_log_armazena_chat_id(db: None) -> None:
    sessao = SessaoConversa.objects.create(chat_id="999@g.us")

    log = LogAuditoria.objects.get(
        modelo="SessaoConversa", objeto_id=sessao.pk, acao="criado"
    )
    assert log.detalhes["chat_id"] == "999@g.us"
