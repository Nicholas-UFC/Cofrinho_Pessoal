import pytest
from django.contrib.auth.models import User

from financas.models import LogAuditoria
from whatsapp.models import SessaoConversa

# ---------------------------------------------------------------------------
# Signals de auditoria — SessaoConversa
# ---------------------------------------------------------------------------
#
# O modelo SessaoConversa armazena o estado da conversa de cada grupo com o
# bot: em qual etapa do fluxo o usuário está, dados temporários da transação
# em andamento, histórico de mensagens recentes e última atividade.
#
# Assim como os modelos financeiros, SessaoConversa está conectada aos signals
# de auditoria do projeto — toda criação, atualização e deleção deve gerar
# um LogAuditoria. Isso permite rastrear quando uma sessão foi criada, quando
# o estado mudou (ex: de "menu" para "aguardando_valor_gasto") e quando foi
# encerrada.
#
# Esta suíte também cobre as operações bulk (`.update()` e `.delete()` via
# queryset), que não disparam signals normais do Django e por isso exigem
# o custom QuerySet do projeto para gerar os logs corretamente.
#
# O teste de detalhes verifica que o `chat_id` é salvo no log, permitindo
# identificar de qual grupo a sessão pertencia mesmo após sua deleção.
# ---------------------------------------------------------------------------


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
