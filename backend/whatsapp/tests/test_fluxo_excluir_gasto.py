from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.test import override_settings

from financas.models import Categoria, Gasto, LogAuditoria
from whatsapp.models import SessaoConversa
from whatsapp.services import processar_mensagem

CHAT_ID = "120363423218993414@g.us"
OWNER = "dono"

# ---------------------------------------------------------------------------
# Exclusão de gastos via WhatsApp
#
# A partir da lista (estado listando_gastos), o usuário digita x<N> para
# iniciar a exclusão do item N da página atual.
#
# Fluxo: lista → x2 → confirmação → s → excluído, volta à lista
#
# Navegação na confirmação:
#   s — confirma e exclui
#   v — volta à lista sem excluir
#   0 — vai ao menu sem excluir
# ---------------------------------------------------------------------------


@pytest.fixture
def usuario(db: None) -> User:
    return User.objects.create_user(username=OWNER, password="pass123")


@pytest.fixture
def categoria(usuario: User) -> Categoria:
    return Categoria.objects.create(nome="Alimentação", usuario=usuario)


@pytest.fixture
def gasto(usuario: User, categoria: Categoria) -> Gasto:
    return Gasto.objects.create(
        usuario=usuario,
        descricao="Almoço",
        valor=Decimal("50.00"),
        categoria=categoria,
        data=date(2026, 4, 1),
    )


def _abrir_lista(chat_id: str = CHAT_ID) -> None:
    processar_mensagem(chat_id, "4")


# ---------------------------------------------------------------------------
# Iniciar exclusão
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_x1_abre_confirmacao(usuario: User, gasto: Gasto) -> None:
    _abrir_lista()
    resposta = processar_mensagem(CHAT_ID, "x1")
    assert "Excluir este gasto" in resposta
    assert "50,00" in resposta
    assert "Alimentação" in resposta
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "confirmando_exclusao_gasto"


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_confirmacao_exibe_criado_e_editado(
    usuario: User, gasto: Gasto
) -> None:
    _abrir_lista()
    resposta = processar_mensagem(CHAT_ID, "x1")
    assert "Criado:" in resposta
    assert "Editado:" in resposta


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_indice_invalido_retorna_erro(usuario: User, gasto: Gasto) -> None:
    _abrir_lista()
    resposta = processar_mensagem(CHAT_ID, "x99")
    assert "inválido" in resposta.lower()
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "listando_gastos"


# ---------------------------------------------------------------------------
# Confirmação — s confirma
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_s_exclui_gasto(usuario: User, gasto: Gasto) -> None:
    _abrir_lista()
    processar_mensagem(CHAT_ID, "x1")
    processar_mensagem(CHAT_ID, "s")
    assert not Gasto.objects.filter(pk=gasto.pk).exists()


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_s_volta_para_lista(usuario: User, gasto: Gasto) -> None:
    _abrir_lista()
    processar_mensagem(CHAT_ID, "x1")
    resposta = processar_mensagem(CHAT_ID, "s")
    assert "excluído" in resposta.lower()
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "listando_gastos"


# ---------------------------------------------------------------------------
# Confirmação — v volta sem excluir
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_v_volta_sem_excluir(usuario: User, gasto: Gasto) -> None:
    _abrir_lista()
    processar_mensagem(CHAT_ID, "x1")
    processar_mensagem(CHAT_ID, "v")
    assert Gasto.objects.filter(pk=gasto.pk).exists()
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "listando_gastos"


# ---------------------------------------------------------------------------
# Confirmação — 0 vai ao menu sem excluir
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_zero_vai_ao_menu_sem_excluir(usuario: User, gasto: Gasto) -> None:
    _abrir_lista()
    processar_mensagem(CHAT_ID, "x1")
    resposta = processar_mensagem(CHAT_ID, "0")
    assert "Cofrinho Pessoal" in resposta
    assert Gasto.objects.filter(pk=gasto.pk).exists()
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "menu"


# ---------------------------------------------------------------------------
# Normalização — X1, x 1, X  1 funcionam como x1
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("cmd", ["X1", "x1"])
@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_normalizacao_x_maiusculo(
    cmd: str, usuario: User, gasto: Gasto
) -> None:
    _abrir_lista()
    resposta = processar_mensagem(CHAT_ID, cmd)
    assert "Excluir este gasto" in resposta


# ---------------------------------------------------------------------------
# Auditoria
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_exclusao_gera_log_auditoria(usuario: User, gasto: Gasto) -> None:
    _abrir_lista()
    processar_mensagem(CHAT_ID, "x1")
    processar_mensagem(CHAT_ID, "s")
    assert LogAuditoria.objects.filter(
        modelo="Gasto", acao="deletado"
    ).exists()


# ---------------------------------------------------------------------------
# Lista atualiza após exclusão
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_lista_atualiza_apos_exclusao(
    usuario: User, categoria: Categoria
) -> None:
    g1 = Gasto.objects.create(
        usuario=usuario,
        descricao="A",
        valor=Decimal("10.00"),
        categoria=categoria,
        data=date(2026, 4, 2),
    )
    g2 = Gasto.objects.create(
        usuario=usuario,
        descricao="B",
        valor=Decimal("20.00"),
        categoria=categoria,
        data=date(2026, 4, 1),
    )
    _abrir_lista()
    processar_mensagem(CHAT_ID, "x1")  # exclui g1 (mais recente)
    resposta = processar_mensagem(CHAT_ID, "s")
    assert not Gasto.objects.filter(pk=g1.pk).exists()
    assert Gasto.objects.filter(pk=g2.pk).exists()
    # Lista retornada deve conter apenas g2
    assert "20,00" in resposta
    assert "10,00" not in resposta
