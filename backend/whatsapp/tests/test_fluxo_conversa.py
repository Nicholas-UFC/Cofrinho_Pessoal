import pytest
from django.contrib.auth.models import User
from django.test import override_settings

from whatsapp.models import SessaoConversa
from whatsapp.services import processar_mensagem

CHAT_ID = "120363423218993414@g.us"
OWNER = "dono"

# ---------------------------------------------------------------------------
# Normalização de entrada e navegação pelo menu do bot
# ---------------------------------------------------------------------------
#
# Este arquivo testa a camada mais superficial do bot: como ele interpreta
# o texto digitado pelo usuário antes de qualquer lógica de negócio.
#
# NORMALIZAÇÃO: o bot aplica `_normalizar_corpo` em toda mensagem recebida,
# que faz `.lower().replace(" ", "")`. Isso significa que "MENU", "M E N U",
# "  menu  " e "mEnU" são todos equivalentes. Esses testes garantem que
# nenhuma variação legítima do comando seja rejeitada por diferença de caixa
# ou espaçamento — comportamento importante num contexto de WhatsApp, onde
# o usuário pode digitar de qualquer forma.
#
# MENU PRINCIPAL: digitar "menu" em qualquer forma exibe o menu completo do
# Cofrinho Pessoal, com as opções de registro de gasto, entrada e resumo.
#
# COMANDOS DESCONHECIDOS: qualquer entrada que não corresponda a um comando
# válido retorna uma mensagem de ajuda listando os comandos disponíveis,
# inclui o texto enviado pelo usuário e não altera o estado da sessão.
#
# Fluxos de gasto e entrada estão em `test_fluxo_gasto.py` e
# `test_fluxo_entrada_resumo.py`.
# ---------------------------------------------------------------------------


@pytest.fixture
def usuario(db: None) -> User:
    return User.objects.create_user(username=OWNER, password="pass123")


# ---------------------------------------------------------------------------
# Normalização de entrada — limpeza antes do processamento
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("entrada", [
    "menu",
    "MENU",
    "Menu",
    "M E N U",
    "M  E  N  U",
    "  menu  ",
    "  M E N U  ",
    "mEnU",
])
@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_menu_aceita_qualquer_forma_de_escrita(
    entrada: str, usuario: User
) -> None:
    resposta = processar_mensagem(CHAT_ID, entrada)
    assert "Cofrinho Pessoal" in resposta
    assert "Registrar gasto" in resposta


# ---------------------------------------------------------------------------
# Menu principal — trigger explícito
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_digitar_menu_minusculo_exibe_menu(usuario: User) -> None:
    resposta = processar_mensagem(CHAT_ID, "menu")
    assert "Cofrinho Pessoal" in resposta
    assert "Registrar gasto" in resposta


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_digitar_menu_maiusculo_exibe_menu(usuario: User) -> None:
    resposta = processar_mensagem(CHAT_ID, "MENU")
    assert "Cofrinho Pessoal" in resposta


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_digitar_menu_misto_exibe_menu(usuario: User) -> None:
    resposta = processar_mensagem(CHAT_ID, "Menu")
    assert "Cofrinho Pessoal" in resposta


# ---------------------------------------------------------------------------
# Comandos desconhecidos
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_comando_desconhecido_retorna_lista_de_comandos(
    usuario: User,
) -> None:
    resposta = processar_mensagem(CHAT_ID, "oi")
    assert "Não conheço o comando" in resposta
    assert "Comandos disponíveis" in resposta
    assert "menu" in resposta


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_numero_invalido_retorna_lista_de_comandos(usuario: User) -> None:
    resposta = processar_mensagem(CHAT_ID, "9")
    assert "Não conheço o comando" in resposta
    assert "Comandos disponíveis" in resposta


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_comando_desconhecido_nao_muda_estado(usuario: User) -> None:
    processar_mensagem(CHAT_ID, "oi")
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "menu"


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_comando_desconhecido_inclui_o_texto_enviado(
    usuario: User,
) -> None:
    resposta = processar_mensagem(CHAT_ID, "teste")
    assert "teste" in resposta
