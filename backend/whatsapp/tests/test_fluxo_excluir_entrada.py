from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.test import override_settings

from financas.models import Entrada, Fonte, LogAuditoria
from whatsapp.models import SessaoConversa
from whatsapp.services import processar_mensagem

CHAT_ID = "120363423218993414@g.us"
OWNER = "dono"

# ---------------------------------------------------------------------------
# Exclusão de entradas via WhatsApp — espelho de test_fluxo_excluir_gasto.py
# ---------------------------------------------------------------------------


@pytest.fixture
def usuario(db: None) -> User:
    return User.objects.create_user(username=OWNER, password="pass123")


@pytest.fixture
def fonte(usuario: User) -> Fonte:
    return Fonte.objects.create(nome="Salário", usuario=usuario)


@pytest.fixture
def entrada(usuario: User, fonte: Fonte) -> Entrada:
    return Entrada.objects.create(
        usuario=usuario,
        descricao="Salário abril",
        valor=Decimal("3000.00"),
        fonte=fonte,
        data=date(2026, 4, 1),
    )


def _abrir_lista(chat_id: str = CHAT_ID) -> None:
    processar_mensagem(chat_id, "5")


# ---------------------------------------------------------------------------
# Iniciar exclusão
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_x1_abre_confirmacao(usuario: User, entrada: Entrada) -> None:
    _abrir_lista()
    resposta = processar_mensagem(CHAT_ID, "x1")
    assert "Excluir esta entrada" in resposta
    assert "3.000,00" in resposta
    assert "Salário" in resposta
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "confirmando_exclusao_entrada"


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_confirmacao_exibe_criado_e_editado(
    usuario: User, entrada: Entrada
) -> None:
    _abrir_lista()
    resposta = processar_mensagem(CHAT_ID, "x1")
    assert "Criado:" in resposta
    assert "Editado:" in resposta


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_indice_invalido_retorna_erro(
    usuario: User, entrada: Entrada
) -> None:
    _abrir_lista()
    resposta = processar_mensagem(CHAT_ID, "x99")
    assert "inválido" in resposta.lower()
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "listando_entradas"


# ---------------------------------------------------------------------------
# Confirmação
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_s_exclui_entrada(usuario: User, entrada: Entrada) -> None:
    _abrir_lista()
    processar_mensagem(CHAT_ID, "x1")
    processar_mensagem(CHAT_ID, "s")
    assert not Entrada.objects.filter(pk=entrada.pk).exists()


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_s_volta_para_lista(usuario: User, entrada: Entrada) -> None:
    _abrir_lista()
    processar_mensagem(CHAT_ID, "x1")
    resposta = processar_mensagem(CHAT_ID, "s")
    assert "excluída" in resposta.lower()
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "listando_entradas"


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_v_volta_sem_excluir(usuario: User, entrada: Entrada) -> None:
    _abrir_lista()
    processar_mensagem(CHAT_ID, "x1")
    processar_mensagem(CHAT_ID, "v")
    assert Entrada.objects.filter(pk=entrada.pk).exists()
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "listando_entradas"


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_zero_vai_ao_menu_sem_excluir(
    usuario: User, entrada: Entrada
) -> None:
    _abrir_lista()
    processar_mensagem(CHAT_ID, "x1")
    resposta = processar_mensagem(CHAT_ID, "0")
    assert "Cofrinho Pessoal" in resposta
    assert Entrada.objects.filter(pk=entrada.pk).exists()
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "menu"


@pytest.mark.parametrize("cmd", ["X1", "x1"])
@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_normalizacao_x_maiusculo(
    cmd: str, usuario: User, entrada: Entrada
) -> None:
    _abrir_lista()
    resposta = processar_mensagem(CHAT_ID, cmd)
    assert "Excluir esta entrada" in resposta


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_exclusao_gera_log_auditoria(
    usuario: User, entrada: Entrada
) -> None:
    _abrir_lista()
    processar_mensagem(CHAT_ID, "x1")
    processar_mensagem(CHAT_ID, "s")
    assert LogAuditoria.objects.filter(
        modelo="Entrada", acao="deletado"
    ).exists()


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_lista_atualiza_apos_exclusao(
    usuario: User, fonte: Fonte
) -> None:
    e1 = Entrada.objects.create(
        usuario=usuario, descricao="A", valor=Decimal("1000.00"),
        fonte=fonte, data=date(2026, 4, 2),
    )
    e2 = Entrada.objects.create(
        usuario=usuario, descricao="B", valor=Decimal("2000.00"),
        fonte=fonte, data=date(2026, 4, 1),
    )
    _abrir_lista()
    processar_mensagem(CHAT_ID, "x1")  # exclui e1 (mais recente)
    resposta = processar_mensagem(CHAT_ID, "s")
    assert not Entrada.objects.filter(pk=e1.pk).exists()
    assert Entrada.objects.filter(pk=e2.pk).exists()
    assert "2.000,00" in resposta
    assert "1.000,00" not in resposta
