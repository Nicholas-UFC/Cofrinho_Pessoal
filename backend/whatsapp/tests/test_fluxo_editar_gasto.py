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
# Edição de gastos via WhatsApp
#
# Fluxo: lista → e<N> → tela de campo → 1(valor) ou 2(categoria)
#        → novo valor/categoria → confirmação → s → atualizado, volta à lista
#
# v na confirmação → volta para tela de campo
# v na tela de campo → volta para a lista
# 0 em qualquer ponto → menu
# ---------------------------------------------------------------------------


@pytest.fixture
def usuario(db: None) -> User:
    return User.objects.create_user(username=OWNER, password="pass123")


@pytest.fixture
def categoria(usuario: User) -> Categoria:
    return Categoria.objects.create(nome="Alimentação", usuario=usuario)


@pytest.fixture
def categoria2(usuario: User) -> Categoria:
    return Categoria.objects.create(nome="Transporte", usuario=usuario)


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
# Abre tela de edição
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_e1_abre_tela_campo(usuario: User, gasto: Gasto) -> None:
    _abrir_lista()
    resposta = processar_mensagem(CHAT_ID, "e1")
    assert "Editando gasto" in resposta
    assert "50,00" in resposta
    assert "Alimentação" in resposta
    assert "Criado:" in resposta
    assert "Editado:" in resposta
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "editando_gasto_campo"


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_indice_invalido_retorna_erro(usuario: User, gasto: Gasto) -> None:
    _abrir_lista()
    resposta = processar_mensagem(CHAT_ID, "e99")
    assert "inválido" in resposta.lower()
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "listando_gastos"


@pytest.mark.parametrize("cmd", ["E1", "e1"])
@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_normalizacao_e_maiusculo(
    cmd: str, usuario: User, gasto: Gasto
) -> None:
    _abrir_lista()
    resposta = processar_mensagem(CHAT_ID, cmd)
    assert "Editando gasto" in resposta


# ---------------------------------------------------------------------------
# Editar valor
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_opcao_1_pede_novo_valor(usuario: User, gasto: Gasto) -> None:
    _abrir_lista()
    processar_mensagem(CHAT_ID, "e1")
    resposta = processar_mensagem(CHAT_ID, "1")
    assert "Novo valor" in resposta
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "editando_gasto_valor"


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_valor_invalido_mantem_estado(usuario: User, gasto: Gasto) -> None:
    _abrir_lista()
    processar_mensagem(CHAT_ID, "e1")
    processar_mensagem(CHAT_ID, "1")
    resposta = processar_mensagem(CHAT_ID, "abc")
    assert "inválido" in resposta.lower()
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "editando_gasto_valor"


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_novo_valor_abre_confirmacao(usuario: User, gasto: Gasto) -> None:
    _abrir_lista()
    processar_mensagem(CHAT_ID, "e1")
    processar_mensagem(CHAT_ID, "1")
    resposta = processar_mensagem(CHAT_ID, "75,00")
    assert "50,00" in resposta  # valor antigo
    assert "75,00" in resposta  # valor novo
    assert "Confirma" in resposta


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_s_salva_novo_valor(usuario: User, gasto: Gasto) -> None:
    _abrir_lista()
    processar_mensagem(CHAT_ID, "e1")
    processar_mensagem(CHAT_ID, "1")
    processar_mensagem(CHAT_ID, "75,00")
    processar_mensagem(CHAT_ID, "s")
    gasto.refresh_from_db()
    assert gasto.valor == Decimal("75.00")


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_s_volta_para_lista(usuario: User, gasto: Gasto) -> None:
    _abrir_lista()
    processar_mensagem(CHAT_ID, "e1")
    processar_mensagem(CHAT_ID, "1")
    processar_mensagem(CHAT_ID, "75,00")
    resposta = processar_mensagem(CHAT_ID, "s")
    assert "atualizado" in resposta.lower()
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "listando_gastos"


# ---------------------------------------------------------------------------
# Editar categoria
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_opcao_2_pede_nova_categoria(
    usuario: User, gasto: Gasto, categoria2: Categoria
) -> None:
    _abrir_lista()
    processar_mensagem(CHAT_ID, "e1")
    resposta = processar_mensagem(CHAT_ID, "2")
    assert "Nova categoria" in resposta
    assert "Transporte" in resposta
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "editando_gasto_categoria"


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_categoria_invalida_mantem_estado(
    usuario: User, gasto: Gasto, categoria2: Categoria
) -> None:
    _abrir_lista()
    processar_mensagem(CHAT_ID, "e1")
    processar_mensagem(CHAT_ID, "2")
    resposta = processar_mensagem(CHAT_ID, "99")
    assert "inválida" in resposta.lower()
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "editando_gasto_categoria"


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_nova_categoria_abre_confirmacao(
    usuario: User, gasto: Gasto, categoria2: Categoria
) -> None:
    _abrir_lista()
    processar_mensagem(CHAT_ID, "e1")
    processar_mensagem(CHAT_ID, "2")
    # Categorias ordenadas por nome: Alimentação(1), Transporte(2)
    resposta = processar_mensagem(CHAT_ID, "2")
    assert "Alimentação" in resposta  # categoria antiga
    assert "Transporte" in resposta  # categoria nova
    assert "Confirma" in resposta


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_s_salva_nova_categoria(
    usuario: User, gasto: Gasto, categoria2: Categoria
) -> None:
    _abrir_lista()
    processar_mensagem(CHAT_ID, "e1")
    processar_mensagem(CHAT_ID, "2")
    processar_mensagem(CHAT_ID, "2")  # seleciona Transporte
    processar_mensagem(CHAT_ID, "s")
    gasto.refresh_from_db()
    assert gasto.categoria == categoria2


# ---------------------------------------------------------------------------
# Navegação com v e 0
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_v_na_confirmacao_volta_para_campo(
    usuario: User, gasto: Gasto
) -> None:
    _abrir_lista()
    processar_mensagem(CHAT_ID, "e1")
    processar_mensagem(CHAT_ID, "1")
    processar_mensagem(CHAT_ID, "75,00")
    resposta = processar_mensagem(CHAT_ID, "v")
    assert "Editando gasto" in resposta
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "editando_gasto_campo"
    # confirmando_campo deve ter sido limpo
    assert "confirmando_campo" not in sessao.dados_temporarios


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_v_no_campo_volta_para_lista(usuario: User, gasto: Gasto) -> None:
    _abrir_lista()
    processar_mensagem(CHAT_ID, "e1")
    resposta = processar_mensagem(CHAT_ID, "v")
    assert "Gastos" in resposta
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "listando_gastos"


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_zero_no_campo_vai_ao_menu(usuario: User, gasto: Gasto) -> None:
    _abrir_lista()
    processar_mensagem(CHAT_ID, "e1")
    resposta = processar_mensagem(CHAT_ID, "0")
    assert "Cofrinho Pessoal" in resposta
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "menu"


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_zero_no_valor_vai_ao_menu(usuario: User, gasto: Gasto) -> None:
    _abrir_lista()
    processar_mensagem(CHAT_ID, "e1")
    processar_mensagem(CHAT_ID, "1")
    resposta = processar_mensagem(CHAT_ID, "0")
    assert "Cofrinho Pessoal" in resposta
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "menu"


# ---------------------------------------------------------------------------
# atualizado_em e auditoria
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_atualizado_em_muda_apos_edicao(usuario: User, gasto: Gasto) -> None:
    antes = gasto.atualizado_em
    _abrir_lista()
    processar_mensagem(CHAT_ID, "e1")
    processar_mensagem(CHAT_ID, "1")
    processar_mensagem(CHAT_ID, "75,00")
    processar_mensagem(CHAT_ID, "s")
    gasto.refresh_from_db()
    assert gasto.atualizado_em >= antes


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_edicao_gera_log_auditoria(usuario: User, gasto: Gasto) -> None:
    _abrir_lista()
    processar_mensagem(CHAT_ID, "e1")
    processar_mensagem(CHAT_ID, "1")
    processar_mensagem(CHAT_ID, "75,00")
    processar_mensagem(CHAT_ID, "s")
    assert LogAuditoria.objects.filter(
        modelo="Gasto", acao="atualizado"
    ).exists()
