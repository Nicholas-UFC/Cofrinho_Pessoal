from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.test import override_settings

from financas.models import Entrada, Fonte, Gasto, Categoria, LogAuditoria
from whatsapp.services import processar_mensagem

CHAT_ID = "120363423218993414@g.us"
OWNER = "dono"

# ---------------------------------------------------------------------------
# Fluxo de entrada financeira, resumo do mês e auditoria via WhatsApp
# ---------------------------------------------------------------------------
#
# Este arquivo cobre três funcionalidades distintas que se complementam:
#
# 1. FLUXO DE ENTRADA: O usuário digita "2" para registrar uma entrada de
#    dinheiro (salário, freelance, renda extra). O fluxo é análogo ao de gasto:
#    valor → fonte → confirmação. O formato monetário é o mesmo padrão
#    brasileiro (ex: "3.000,00"). Confirmação com "s" salva o registro,
#    "n" cancela sem persistir nada.
#
# 2. RESUMO DO MÊS: O usuário digita "3" para ver o balanço financeiro do mês
#    atual. O bot retorna total de entradas, total de gastos e saldo (entradas
#    menos gastos). Os valores são formatados em reais e devem bater com os
#    registros do banco para o usuário autenticado.
#
# 3. AUDITORIA: Toda operação de criação de Gasto ou Entrada via WhatsApp deve
#    gerar um LogAuditoria com acao="criado". Isso garante rastreabilidade
#    completa — é possível saber que o registro veio do bot do WhatsApp e não
#    de outra interface.
# ---------------------------------------------------------------------------


@pytest.fixture
def usuario(db: None) -> User:
    return User.objects.create_user(username=OWNER, password="pass123")


@pytest.fixture
def categoria(usuario: User) -> Categoria:
    return Categoria.objects.create(nome="Alimentação", usuario=usuario)


@pytest.fixture
def fonte(usuario: User) -> Fonte:
    return Fonte.objects.create(nome="Salário", usuario=usuario)


# ---------------------------------------------------------------------------
# Fluxo de entrada
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_opcao_2_solicita_valor(usuario: User) -> None:
    resposta = processar_mensagem(CHAT_ID, "2")
    assert "valor da entrada" in resposta.lower()

    from whatsapp.models import SessaoConversa
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "aguardando_valor_entrada"


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_fluxo_entrada_completa(usuario: User, fonte: Fonte) -> None:
    processar_mensagem(CHAT_ID, "2")
    processar_mensagem(CHAT_ID, "3.000,00")
    processar_mensagem(CHAT_ID, "1")
    resposta = processar_mensagem(CHAT_ID, "s")

    assert "registrada" in resposta.lower()
    assert Entrada.objects.filter(
        usuario=usuario, valor=Decimal("3000.00")
    ).exists()


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_fluxo_entrada_cancelada(usuario: User, fonte: Fonte) -> None:
    processar_mensagem(CHAT_ID, "2")
    processar_mensagem(CHAT_ID, "3.000,00")
    processar_mensagem(CHAT_ID, "1")
    resposta = processar_mensagem(CHAT_ID, "n")

    assert "cancelado" in resposta.lower()
    assert not Entrada.objects.filter(usuario=usuario).exists()


# ---------------------------------------------------------------------------
# Resumo do mês
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_resumo_do_mes(
    usuario: User, categoria: Categoria, fonte: Fonte
) -> None:
    # Cria registros diretamente no banco para simular histórico do mês atual.
    # O bot deve somar entradas, somar gastos e calcular o saldo.
    hoje = date.today()
    Gasto.objects.create(
        usuario=usuario,
        descricao="Teste",
        valor=Decimal("100.00"),
        categoria=categoria,
        data=hoje,
    )
    Entrada.objects.create(
        usuario=usuario,
        descricao="Teste",
        valor=Decimal("500.00"),
        fonte=fonte,
        data=hoje,
    )

    resposta = processar_mensagem(CHAT_ID, "3")
    assert "100.00" in resposta
    assert "500.00" in resposta
    assert "400.00" in resposta


# ---------------------------------------------------------------------------
# Auditoria — operações via WhatsApp geram LogAuditoria
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_gasto_via_whatsapp_gera_log_auditoria(
    usuario: User, categoria: Categoria
) -> None:
    processar_mensagem(CHAT_ID, "1")
    processar_mensagem(CHAT_ID, "50,00")
    processar_mensagem(CHAT_ID, "1")
    processar_mensagem(CHAT_ID, "s")

    assert LogAuditoria.objects.filter(
        modelo="Gasto", acao="criado"
    ).exists()


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_entrada_via_whatsapp_gera_log_auditoria(
    usuario: User, fonte: Fonte
) -> None:
    processar_mensagem(CHAT_ID, "2")
    processar_mensagem(CHAT_ID, "1.500,00")
    processar_mensagem(CHAT_ID, "1")
    processar_mensagem(CHAT_ID, "s")

    assert LogAuditoria.objects.filter(
        modelo="Entrada", acao="criado"
    ).exists()
