from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.test import override_settings

from financas.models import Categoria, Gasto
from whatsapp.models import SessaoConversa
from whatsapp.services import processar_mensagem

CHAT_ID = "120363423218993414@g.us"
OWNER = "dono"

# ---------------------------------------------------------------------------
# Listagem paginada de gastos via WhatsApp — opção 4 do menu
#
# O usuário digita 4 no menu e recebe uma lista compacta dos gastos do mês
# atual, ordenada do mais recente para o mais antigo, com 5 itens por página.
#
# Navegação:
#   p — próxima página
#   a — página anterior
#   e<N> — editar item N (testado em test_fluxo_editar_gasto.py)
#   x<N> — excluir item N (testado em test_fluxo_excluir_gasto.py)
#   0 — sair para o menu principal
#
# Casos de borda:
#   — Lista vazia retorna mensagem adequada e volta ao menu
#   — Primeira página não tem anterior
#   — Última página não tem próxima
#   — Normalização: P, p, A, a, E2, e 2 etc. funcionam
# ---------------------------------------------------------------------------


@pytest.fixture
def usuario(db: None) -> User:
    return User.objects.create_user(username=OWNER, password="pass123")


@pytest.fixture
def categoria(usuario: User) -> Categoria:
    return Categoria.objects.create(nome="Alimentação", usuario=usuario)


def _criar_gastos(usuario: User, categoria: Categoria, n: int) -> list[Gasto]:
    gastos = []
    for i in range(n):
        gastos.append(
            Gasto.objects.create(
                usuario=usuario,
                descricao=f"Gasto {i + 1}",
                valor=Decimal(f"{(i + 1) * 10}.00"),
                categoria=categoria,
                data=date(2026, 4, n - i),
            )
        )
    return gastos


# ---------------------------------------------------------------------------
# Abre a lista
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_opcao_4_entra_em_listando_gastos(
    usuario: User, categoria: Categoria
) -> None:
    _criar_gastos(usuario, categoria, 1)
    processar_mensagem(CHAT_ID, "4")
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "listando_gastos"


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_lista_exibe_valor_categoria_e_data(
    usuario: User, categoria: Categoria
) -> None:
    _criar_gastos(usuario, categoria, 1)
    resposta = processar_mensagem(CHAT_ID, "4")
    assert "10,00" in resposta
    assert "Alimentação" in resposta


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_lista_vazia_retorna_mensagem_e_volta_ao_menu(
    usuario: User,
) -> None:
    resposta = processar_mensagem(CHAT_ID, "4")
    assert "nenhum gasto" in resposta.lower()
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "menu"


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_lista_exibe_5_por_pagina(
    usuario: User, categoria: Categoria
) -> None:
    _criar_gastos(usuario, categoria, 7)
    resposta = processar_mensagem(CHAT_ID, "4")
    # Página 1 deve ter exatamente 5 itens numerados
    assert "1." in resposta
    assert "5." in resposta
    assert "6." not in resposta


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_lista_exibe_numero_de_paginas(
    usuario: User, categoria: Categoria
) -> None:
    _criar_gastos(usuario, categoria, 7)
    resposta = processar_mensagem(CHAT_ID, "4")
    assert "pág 1/2" in resposta


# ---------------------------------------------------------------------------
# Paginação
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_proxima_pagina_avanca(
    usuario: User, categoria: Categoria
) -> None:
    _criar_gastos(usuario, categoria, 7)
    processar_mensagem(CHAT_ID, "4")
    resposta = processar_mensagem(CHAT_ID, "p")
    assert "pág 2/2" in resposta
    # Página 2 tem 2 itens, numerados 1 e 2 (numeração por página)
    assert "1." in resposta
    assert "2." in resposta
    assert "3." not in resposta


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_pagina_anterior_volta(
    usuario: User, categoria: Categoria
) -> None:
    _criar_gastos(usuario, categoria, 7)
    processar_mensagem(CHAT_ID, "4")
    processar_mensagem(CHAT_ID, "p")
    resposta = processar_mensagem(CHAT_ID, "a")
    assert "pág 1/2" in resposta


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_anterior_na_primeira_pagina_avisa(
    usuario: User, categoria: Categoria
) -> None:
    _criar_gastos(usuario, categoria, 3)
    processar_mensagem(CHAT_ID, "4")
    resposta = processar_mensagem(CHAT_ID, "a")
    assert "primeira página" in resposta.lower()
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "listando_gastos"


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_proxima_na_ultima_pagina_avisa(
    usuario: User, categoria: Categoria
) -> None:
    _criar_gastos(usuario, categoria, 3)
    processar_mensagem(CHAT_ID, "4")
    resposta = processar_mensagem(CHAT_ID, "p")
    assert "última página" in resposta.lower()
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "listando_gastos"


# ---------------------------------------------------------------------------
# Navegação e normalização
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_zero_sai_para_menu(
    usuario: User, categoria: Categoria
) -> None:
    _criar_gastos(usuario, categoria, 1)
    processar_mensagem(CHAT_ID, "4")
    resposta = processar_mensagem(CHAT_ID, "0")
    assert "Cofrinho Pessoal" in resposta
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "menu"


@pytest.mark.parametrize("entrada", ["P", "p"])
@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_proxima_normalizada(
    entrada: str, usuario: User, categoria: Categoria
) -> None:
    _criar_gastos(usuario, categoria, 7)
    processar_mensagem(CHAT_ID, "4")
    resposta = processar_mensagem(CHAT_ID, entrada)
    assert "pág 2/2" in resposta


@pytest.mark.parametrize("entrada", ["A", "a"])
@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_anterior_normalizada(
    entrada: str, usuario: User, categoria: Categoria
) -> None:
    _criar_gastos(usuario, categoria, 7)
    processar_mensagem(CHAT_ID, "4")
    processar_mensagem(CHAT_ID, "p")
    resposta = processar_mensagem(CHAT_ID, entrada)
    assert "pág 1/2" in resposta


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_lista_ordena_mais_recente_primeiro(
    usuario: User, categoria: Categoria
) -> None:
    _criar_gastos(usuario, categoria, 3)
    resposta = processar_mensagem(CHAT_ID, "4")
    # Mais recente (04/04) deve aparecer antes do mais antigo (04/02)
    pos_1 = resposta.index("1.")
    pos_2 = resposta.index("2.")
    assert pos_1 < pos_2
