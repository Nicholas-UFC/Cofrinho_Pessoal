from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.test import override_settings

from financas.models import Categoria, Gasto
from whatsapp.services import processar_mensagem

CHAT_ID = "120363423218993414@g.us"
OWNER = "dono"

# ---------------------------------------------------------------------------
# Fluxo de registro de gasto via WhatsApp
# ---------------------------------------------------------------------------
#
# Este arquivo testa o fluxo completo de registro de um gasto pelo bot do
# Cofrinho Pessoal no WhatsApp. O fluxo é conversacional e multi-etapa:
#
#   1. Usuário digita "1" → bot pede o valor do gasto
#   2. Usuário digita o valor (ex: "25,50") → bot pede a categoria
#   3. Usuário digita o número da categoria → bot pede confirmação
#   4. Usuário confirma com "s" → gasto registrado / cancela com "n" → cancelado
#
# Casos de borda testados:
# — Valor inválido (texto, negativo, zero): estado deve permanecer na mesma etapa
# — Valor com espaçamento: "25 , 50", "5 . 000 , 50" etc. devem ser aceitos após
#   normalização — espaços são removidos antes do parse do valor monetário
# — Categoria inexistente: deve manter estado e pedir novamente
# — Cancelar em qualquer etapa com "0": retorna ao menu principal sem salvar nada
#
# O valor monetário aceito segue o padrão brasileiro:
# — Separador de milhar: ponto (somente grupos de 3 dígitos)
# — Separador decimal: vírgula (exatamente 2 casas, ou nenhuma)
# — Exemplos válidos: "25", "25,50", "1.000", "5.000,50", "1.000.000,00"
# ---------------------------------------------------------------------------


@pytest.fixture
def usuario(db: None) -> User:
    return User.objects.create_user(username=OWNER, password="pass123")


@pytest.fixture
def categoria(usuario: User) -> Categoria:
    return Categoria.objects.create(nome="Alimentação", usuario=usuario)


# ---------------------------------------------------------------------------
# Valores com espaços — devem ser aceitos após normalização
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("valor_digitado,valor_esperado", [
    ("25, 50",          Decimal("25.50")),   # espaço após vírgula
    ("25 , 50",         Decimal("25.50")),   # espaços ao redor da vírgula
    ("25 .000",         Decimal("25000.00")), # espaço antes do ponto
    ("25. 000",         Decimal("25000.00")), # espaço após o ponto
    ("5 . 000 , 50",    Decimal("5000.50")),  # espaços em todo lugar
    ("  25,50  ",       Decimal("25.50")),    # espaços nas bordas
])
@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_valor_com_espacos_e_aceito(
    valor_digitado: str, valor_esperado: Decimal, usuario: User, categoria: Categoria
) -> None:
    """Espaços no valor monetário são ignorados antes da validação."""
    processar_mensagem(CHAT_ID, "1")
    processar_mensagem(CHAT_ID, valor_digitado)
    processar_mensagem(CHAT_ID, "1")
    processar_mensagem(CHAT_ID, "s")
    assert Gasto.objects.filter(usuario=usuario, valor=valor_esperado).exists()


# ---------------------------------------------------------------------------
# Início do fluxo — opção "1" no menu
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_opcao_1_solicita_valor(usuario: User) -> None:
    resposta = processar_mensagem(CHAT_ID, "1")
    assert "valor do gasto" in resposta.lower()

    from whatsapp.models import SessaoConversa
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "aguardando_valor_gasto"


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_valor_gasto_invalido_mantem_estado(usuario: User) -> None:
    processar_mensagem(CHAT_ID, "1")
    resposta = processar_mensagem(CHAT_ID, "abc")
    assert "inválido" in resposta.lower()

    from whatsapp.models import SessaoConversa
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "aguardando_valor_gasto"


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_cancelar_no_valor_volta_ao_menu(usuario: User) -> None:
    processar_mensagem(CHAT_ID, "1")
    resposta = processar_mensagem(CHAT_ID, "0")
    assert "Cofrinho Pessoal" in resposta

    from whatsapp.models import SessaoConversa
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "menu"


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_categoria_invalida_mantem_estado(
    usuario: User, categoria: Categoria
) -> None:
    processar_mensagem(CHAT_ID, "1")
    processar_mensagem(CHAT_ID, "25,50")
    resposta = processar_mensagem(CHAT_ID, "99")
    assert "inválida" in resposta.lower()

    from whatsapp.models import SessaoConversa
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "aguardando_categoria_gasto"


# ---------------------------------------------------------------------------
# Fluxo completo
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_fluxo_gasto_completo(usuario: User, categoria: Categoria) -> None:
    processar_mensagem(CHAT_ID, "1")
    processar_mensagem(CHAT_ID, "25,50")
    processar_mensagem(CHAT_ID, "1")
    resposta = processar_mensagem(CHAT_ID, "s")

    assert "registrado" in resposta.lower()
    assert Gasto.objects.filter(
        usuario=usuario, valor=Decimal("25.50")
    ).exists()

    from whatsapp.models import SessaoConversa
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "menu"


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_fluxo_gasto_cancelado_na_confirmacao(
    usuario: User, categoria: Categoria
) -> None:
    processar_mensagem(CHAT_ID, "1")
    processar_mensagem(CHAT_ID, "25,50")
    processar_mensagem(CHAT_ID, "1")
    resposta = processar_mensagem(CHAT_ID, "n")

    assert "cancelado" in resposta.lower()
    assert not Gasto.objects.filter(usuario=usuario).exists()

    from whatsapp.models import SessaoConversa
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "menu"
