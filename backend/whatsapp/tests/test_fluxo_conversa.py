from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.test import override_settings

from financas.models import Categoria, Entrada, Fonte, Gasto, LogAuditoria
from whatsapp.models import SessaoConversa
from whatsapp.services import processar_mensagem

CHAT_ID = "120363423218993414@g.us"
OWNER = "dono"


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
# Menu principal
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_mensagem_desconhecida_exibe_menu(usuario: User) -> None:
    resposta = processar_mensagem(CHAT_ID, "oi")
    assert "Cofrinho Pessoal" in resposta
    assert "Registrar gasto" in resposta


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_opcao_invalida_exibe_menu(usuario: User) -> None:
    resposta = processar_mensagem(CHAT_ID, "9")
    assert "Cofrinho Pessoal" in resposta


# ---------------------------------------------------------------------------
# Fluxo de gasto
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_opcao_1_solicita_valor(usuario: User) -> None:
    resposta = processar_mensagem(CHAT_ID, "1")
    assert "valor do gasto" in resposta.lower()
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "aguardando_valor_gasto"


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_valor_gasto_invalido_mantem_estado(usuario: User) -> None:
    processar_mensagem(CHAT_ID, "1")
    resposta = processar_mensagem(CHAT_ID, "abc")
    assert "inválido" in resposta.lower()
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "aguardando_valor_gasto"


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_cancelar_no_valor_volta_ao_menu(usuario: User) -> None:
    processar_mensagem(CHAT_ID, "1")
    resposta = processar_mensagem(CHAT_ID, "0")
    assert "Cofrinho Pessoal" in resposta
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "menu"


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_categoria_invalida_mantem_estado(
    usuario: User, categoria: Categoria
) -> None:
    processar_mensagem(CHAT_ID, "1")
    processar_mensagem(CHAT_ID, "25.50")
    resposta = processar_mensagem(CHAT_ID, "99")
    assert "inválida" in resposta.lower()
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "aguardando_categoria_gasto"


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_fluxo_gasto_completo(usuario: User, categoria: Categoria) -> None:
    processar_mensagem(CHAT_ID, "1")
    processar_mensagem(CHAT_ID, "25.50")
    processar_mensagem(CHAT_ID, "1")
    resposta = processar_mensagem(CHAT_ID, "s")

    assert "registrado" in resposta.lower()
    assert Gasto.objects.filter(
        usuario=usuario, valor=Decimal("25.50")
    ).exists()
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "menu"


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_fluxo_gasto_cancelado_na_confirmacao(
    usuario: User, categoria: Categoria
) -> None:
    processar_mensagem(CHAT_ID, "1")
    processar_mensagem(CHAT_ID, "25.50")
    processar_mensagem(CHAT_ID, "1")
    resposta = processar_mensagem(CHAT_ID, "n")

    assert "cancelado" in resposta.lower()
    assert not Gasto.objects.filter(usuario=usuario).exists()
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "menu"


# ---------------------------------------------------------------------------
# Fluxo de entrada
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_opcao_2_solicita_valor(usuario: User) -> None:
    resposta = processar_mensagem(CHAT_ID, "2")
    assert "valor da entrada" in resposta.lower()
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "aguardando_valor_entrada"


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_fluxo_entrada_completa(usuario: User, fonte: Fonte) -> None:
    processar_mensagem(CHAT_ID, "2")
    processar_mensagem(CHAT_ID, "3000.00")
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
    processar_mensagem(CHAT_ID, "3000.00")
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
# Gasto/entrada geram LogAuditoria
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_gasto_via_whatsapp_gera_log_auditoria(
    usuario: User, categoria: Categoria
) -> None:
    processar_mensagem(CHAT_ID, "1")
    processar_mensagem(CHAT_ID, "50.00")
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
    processar_mensagem(CHAT_ID, "1500.00")
    processar_mensagem(CHAT_ID, "1")
    processar_mensagem(CHAT_ID, "s")

    assert LogAuditoria.objects.filter(
        modelo="Entrada", acao="criado"
    ).exists()
