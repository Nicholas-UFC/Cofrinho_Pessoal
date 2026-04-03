from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.test import override_settings

from financas.models import Entrada, Fonte
from whatsapp.models import SessaoConversa
from whatsapp.services import processar_mensagem

CHAT_ID = "120363423218993414@g.us"
OWNER = "dono"

# ---------------------------------------------------------------------------
# Listagem paginada de entradas via WhatsApp — opção 5 do menu
#
# Espelho de test_fluxo_listar_gastos.py, com Entrada e Fonte no lugar
# de Gasto e Categoria. Mesma lógica de paginação, ordenação e navegação.
# ---------------------------------------------------------------------------


@pytest.fixture
def usuario(db: None) -> User:
    return User.objects.create_user(username=OWNER, password="pass123")


@pytest.fixture
def fonte(usuario: User) -> Fonte:
    return Fonte.objects.create(nome="Salário", usuario=usuario)


def _criar_entradas(usuario: User, fonte: Fonte, n: int) -> list[Entrada]:
    entradas = []
    for i in range(n):
        entradas.append(
            Entrada.objects.create(
                usuario=usuario,
                descricao=f"Entrada {i + 1}",
                valor=Decimal(f"{(i + 1) * 100}.00"),
                fonte=fonte,
                data=date(2026, 4, n - i),
            )
        )
    return entradas


# ---------------------------------------------------------------------------
# Abre a lista
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_opcao_5_entra_em_listando_entradas(
    usuario: User, fonte: Fonte
) -> None:
    _criar_entradas(usuario, fonte, 1)
    processar_mensagem(CHAT_ID, "5")
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "listando_entradas"


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_lista_exibe_valor_fonte_e_data(usuario: User, fonte: Fonte) -> None:
    _criar_entradas(usuario, fonte, 1)
    resposta = processar_mensagem(CHAT_ID, "5")
    assert "100,00" in resposta
    assert "Salário" in resposta


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_lista_vazia_retorna_mensagem_e_volta_ao_menu(
    usuario: User,
) -> None:
    resposta = processar_mensagem(CHAT_ID, "5")
    assert "nenhuma entrada" in resposta.lower()
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "menu"


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_lista_exibe_5_por_pagina(usuario: User, fonte: Fonte) -> None:
    _criar_entradas(usuario, fonte, 7)
    resposta = processar_mensagem(CHAT_ID, "5")
    assert "1." in resposta
    assert "5." in resposta
    assert "6." not in resposta


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_lista_exibe_numero_de_paginas(usuario: User, fonte: Fonte) -> None:
    _criar_entradas(usuario, fonte, 7)
    resposta = processar_mensagem(CHAT_ID, "5")
    assert "pág 1/2" in resposta


# ---------------------------------------------------------------------------
# Paginação
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_proxima_pagina_avanca(usuario: User, fonte: Fonte) -> None:
    _criar_entradas(usuario, fonte, 7)
    processar_mensagem(CHAT_ID, "5")
    resposta = processar_mensagem(CHAT_ID, "p")
    assert "pág 2/2" in resposta
    # Página 2 tem 2 itens, numerados 1 e 2 (numeração por página)
    assert "1." in resposta
    assert "2." in resposta
    assert "3." not in resposta


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_pagina_anterior_volta(usuario: User, fonte: Fonte) -> None:
    _criar_entradas(usuario, fonte, 7)
    processar_mensagem(CHAT_ID, "5")
    processar_mensagem(CHAT_ID, "p")
    resposta = processar_mensagem(CHAT_ID, "a")
    assert "pág 1/2" in resposta


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_anterior_na_primeira_pagina_avisa(
    usuario: User, fonte: Fonte
) -> None:
    _criar_entradas(usuario, fonte, 3)
    processar_mensagem(CHAT_ID, "5")
    resposta = processar_mensagem(CHAT_ID, "a")
    assert "primeira página" in resposta.lower()
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "listando_entradas"


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_proxima_na_ultima_pagina_avisa(usuario: User, fonte: Fonte) -> None:
    _criar_entradas(usuario, fonte, 3)
    processar_mensagem(CHAT_ID, "5")
    resposta = processar_mensagem(CHAT_ID, "p")
    assert "última página" in resposta.lower()
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "listando_entradas"


# ---------------------------------------------------------------------------
# Navegação e normalização
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_zero_sai_para_menu(usuario: User, fonte: Fonte) -> None:
    _criar_entradas(usuario, fonte, 1)
    processar_mensagem(CHAT_ID, "5")
    resposta = processar_mensagem(CHAT_ID, "0")
    assert "Cofrinho Pessoal" in resposta
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "menu"


@pytest.mark.parametrize("entrada_cmd", ["P", "p"])
@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_proxima_normalizada(
    entrada_cmd: str, usuario: User, fonte: Fonte
) -> None:
    _criar_entradas(usuario, fonte, 7)
    processar_mensagem(CHAT_ID, "5")
    resposta = processar_mensagem(CHAT_ID, entrada_cmd)
    assert "pág 2/2" in resposta


@pytest.mark.parametrize("entrada_cmd", ["A", "a"])
@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_anterior_normalizada(
    entrada_cmd: str, usuario: User, fonte: Fonte
) -> None:
    _criar_entradas(usuario, fonte, 7)
    processar_mensagem(CHAT_ID, "5")
    processar_mensagem(CHAT_ID, "p")
    resposta = processar_mensagem(CHAT_ID, entrada_cmd)
    assert "pág 1/2" in resposta


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_lista_ordena_mais_recente_primeiro(
    usuario: User, fonte: Fonte
) -> None:
    _criar_entradas(usuario, fonte, 3)
    resposta = processar_mensagem(CHAT_ID, "5")
    pos_1 = resposta.index("1.")
    pos_2 = resposta.index("2.")
    assert pos_1 < pos_2
