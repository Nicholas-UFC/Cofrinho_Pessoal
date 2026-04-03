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
# Edição de entradas via WhatsApp — espelho de test_fluxo_editar_gasto.py
# ---------------------------------------------------------------------------


@pytest.fixture
def usuario(db: None) -> User:
    return User.objects.create_user(username=OWNER, password="pass123")


@pytest.fixture
def fonte(usuario: User) -> Fonte:
    return Fonte.objects.create(nome="Salário", usuario=usuario)


@pytest.fixture
def fonte2(usuario: User) -> Fonte:
    return Fonte.objects.create(nome="Freelance", usuario=usuario)


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
# Abre tela de edição
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_e1_abre_tela_campo(usuario: User, entrada: Entrada) -> None:
    _abrir_lista()
    resposta = processar_mensagem(CHAT_ID, "e1")
    assert "Editando entrada" in resposta
    assert "3.000,00" in resposta
    assert "Salário" in resposta
    assert "Criado:" in resposta
    assert "Editado:" in resposta
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "editando_entrada_campo"


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_indice_invalido_retorna_erro(usuario: User, entrada: Entrada) -> None:
    _abrir_lista()
    resposta = processar_mensagem(CHAT_ID, "e99")
    assert "inválido" in resposta.lower()
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "listando_entradas"


@pytest.mark.parametrize("cmd", ["E1", "e1"])
@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_normalizacao_e_maiusculo(
    cmd: str, usuario: User, entrada: Entrada
) -> None:
    _abrir_lista()
    resposta = processar_mensagem(CHAT_ID, cmd)
    assert "Editando entrada" in resposta


# ---------------------------------------------------------------------------
# Editar valor
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_opcao_1_pede_novo_valor(usuario: User, entrada: Entrada) -> None:
    _abrir_lista()
    processar_mensagem(CHAT_ID, "e1")
    resposta = processar_mensagem(CHAT_ID, "1")
    assert "Novo valor" in resposta
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "editando_entrada_valor"


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_valor_invalido_mantem_estado(usuario: User, entrada: Entrada) -> None:
    _abrir_lista()
    processar_mensagem(CHAT_ID, "e1")
    processar_mensagem(CHAT_ID, "1")
    resposta = processar_mensagem(CHAT_ID, "abc")
    assert "inválido" in resposta.lower()
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "editando_entrada_valor"


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_novo_valor_abre_confirmacao(usuario: User, entrada: Entrada) -> None:
    _abrir_lista()
    processar_mensagem(CHAT_ID, "e1")
    processar_mensagem(CHAT_ID, "1")
    resposta = processar_mensagem(CHAT_ID, "3.500,00")
    assert "3.000,00" in resposta  # valor antigo
    assert "3.500,00" in resposta  # valor novo
    assert "Confirma" in resposta


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_s_salva_novo_valor(usuario: User, entrada: Entrada) -> None:
    _abrir_lista()
    processar_mensagem(CHAT_ID, "e1")
    processar_mensagem(CHAT_ID, "1")
    processar_mensagem(CHAT_ID, "3.500,00")
    processar_mensagem(CHAT_ID, "s")
    entrada.refresh_from_db()
    assert entrada.valor == Decimal("3500.00")


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_s_volta_para_lista(usuario: User, entrada: Entrada) -> None:
    _abrir_lista()
    processar_mensagem(CHAT_ID, "e1")
    processar_mensagem(CHAT_ID, "1")
    processar_mensagem(CHAT_ID, "3.500,00")
    resposta = processar_mensagem(CHAT_ID, "s")
    assert "atualizada" in resposta.lower()
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "listando_entradas"


# ---------------------------------------------------------------------------
# Editar fonte
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_opcao_2_pede_nova_fonte(
    usuario: User, entrada: Entrada, fonte2: Fonte
) -> None:
    _abrir_lista()
    processar_mensagem(CHAT_ID, "e1")
    resposta = processar_mensagem(CHAT_ID, "2")
    assert "Nova fonte" in resposta
    assert "Freelance" in resposta
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "editando_entrada_fonte"


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_fonte_invalida_mantem_estado(
    usuario: User, entrada: Entrada, fonte2: Fonte
) -> None:
    _abrir_lista()
    processar_mensagem(CHAT_ID, "e1")
    processar_mensagem(CHAT_ID, "2")
    resposta = processar_mensagem(CHAT_ID, "99")
    assert "inválida" in resposta.lower()
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "editando_entrada_fonte"


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_nova_fonte_abre_confirmacao(
    usuario: User, entrada: Entrada, fonte2: Fonte
) -> None:
    _abrir_lista()
    processar_mensagem(CHAT_ID, "e1")
    processar_mensagem(CHAT_ID, "2")
    # Fontes ordenadas por nome: Freelance(1), Salário(2)
    resposta = processar_mensagem(CHAT_ID, "1")
    assert "Salário" in resposta  # fonte antiga
    assert "Freelance" in resposta  # fonte nova
    assert "Confirma" in resposta


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_s_salva_nova_fonte(
    usuario: User, entrada: Entrada, fonte2: Fonte
) -> None:
    _abrir_lista()
    processar_mensagem(CHAT_ID, "e1")
    processar_mensagem(CHAT_ID, "2")
    processar_mensagem(CHAT_ID, "1")  # seleciona Freelance
    processar_mensagem(CHAT_ID, "s")
    entrada.refresh_from_db()
    assert entrada.fonte == fonte2


# ---------------------------------------------------------------------------
# Navegação com v e 0
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_v_na_confirmacao_volta_para_campo(
    usuario: User, entrada: Entrada
) -> None:
    _abrir_lista()
    processar_mensagem(CHAT_ID, "e1")
    processar_mensagem(CHAT_ID, "1")
    processar_mensagem(CHAT_ID, "3.500,00")
    resposta = processar_mensagem(CHAT_ID, "v")
    assert "Editando entrada" in resposta
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "editando_entrada_campo"
    assert "confirmando_campo" not in sessao.dados_temporarios


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_v_no_campo_volta_para_lista(usuario: User, entrada: Entrada) -> None:
    _abrir_lista()
    processar_mensagem(CHAT_ID, "e1")
    resposta = processar_mensagem(CHAT_ID, "v")
    assert "Entradas" in resposta
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "listando_entradas"


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_zero_no_campo_vai_ao_menu(usuario: User, entrada: Entrada) -> None:
    _abrir_lista()
    processar_mensagem(CHAT_ID, "e1")
    resposta = processar_mensagem(CHAT_ID, "0")
    assert "Cofrinho Pessoal" in resposta
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "menu"


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_zero_no_valor_vai_ao_menu(usuario: User, entrada: Entrada) -> None:
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
def test_atualizado_em_muda_apos_edicao(
    usuario: User, entrada: Entrada
) -> None:
    antes = entrada.atualizado_em
    _abrir_lista()
    processar_mensagem(CHAT_ID, "e1")
    processar_mensagem(CHAT_ID, "1")
    processar_mensagem(CHAT_ID, "3.500,00")
    processar_mensagem(CHAT_ID, "s")
    entrada.refresh_from_db()
    assert entrada.atualizado_em >= antes


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_edicao_gera_log_auditoria(usuario: User, entrada: Entrada) -> None:
    _abrir_lista()
    processar_mensagem(CHAT_ID, "e1")
    processar_mensagem(CHAT_ID, "1")
    processar_mensagem(CHAT_ID, "3.500,00")
    processar_mensagem(CHAT_ID, "s")
    assert LogAuditoria.objects.filter(
        modelo="Entrada", acao="atualizado"
    ).exists()
