"""
Ponto de entrada do CRUD via WhatsApp.

Expõe:
  abrir_lista_gastos / abrir_lista_entradas — chamados pelo menu (4/5)
  processar_estado_crud — chamado pelo dispatcher para estados de CRUD
"""
import math

from financas.models import Entrada, Gasto
from whatsapp.models import SessaoConversa
from whatsapp.services.utils import MENU_TEXTO, _obter_usuario, _resetar

ITENS_POR_PAGINA = 5


# ---------------------------------------------------------------------------
# Formatação compacta (usada por listagem, exclusão e edição)
# ---------------------------------------------------------------------------


def fmt_valor(valor) -> str:  # noqa: ANN001
    """Converte Decimal para formato BR: 1.500,00."""
    return (
        f"{valor:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def fmt_item_gasto(idx: int, gasto: Gasto) -> str:
    data = gasto.data.strftime("%d/%m")
    return f"{idx}. R$ {fmt_valor(gasto.valor)} | {gasto.categoria.nome} | {data}"


def fmt_item_entrada(idx: int, entrada: Entrada) -> str:
    data = entrada.data.strftime("%d/%m")
    return (
        f"{idx}. R$ {fmt_valor(entrada.valor)} | {entrada.fonte.nome} | {data}"
    )


def rodape_lista(pagina: int, total: int) -> str:
    nav = []
    if pagina < total:
        nav.append("p próxima")
    if pagina > 1:
        nav.append("a anterior")
    nav.append("0 sair")
    return "e<N> editar · x<N> excluir\n" + " · ".join(nav)


def montar_lista_gastos(
    gastos: list[Gasto], pagina: int, total_paginas: int
) -> str:
    inicio = (pagina - 1) * ITENS_POR_PAGINA
    fatia = gastos[inicio: inicio + ITENS_POR_PAGINA]
    linhas = [fmt_item_gasto(i + 1, g) for i, g in enumerate(fatia)]
    return (
        f"*Gastos — pág {pagina}/{total_paginas}*\n"
        + "\n".join(linhas)
        + "\n\n"
        + rodape_lista(pagina, total_paginas)
    )


def montar_lista_entradas(
    entradas: list[Entrada], pagina: int, total_paginas: int
) -> str:
    inicio = (pagina - 1) * ITENS_POR_PAGINA
    fatia = entradas[inicio: inicio + ITENS_POR_PAGINA]
    linhas = [fmt_item_entrada(i + 1, e) for i, e in enumerate(fatia)]
    return (
        f"*Entradas — pág {pagina}/{total_paginas}*\n"
        + "\n".join(linhas)
        + "\n\n"
        + rodape_lista(pagina, total_paginas)
    )


def total_paginas_gastos(gastos: list) -> int:
    return max(1, math.ceil(len(gastos) / ITENS_POR_PAGINA))


def total_paginas_entradas(entradas: list) -> int:
    return max(1, math.ceil(len(entradas) / ITENS_POR_PAGINA))


def carregar_gastos(usuario) -> list[Gasto]:  # noqa: ANN001
    return list(
        Gasto.objects.filter(usuario=usuario)
        .order_by("-data", "-criado_em")
        .select_related("categoria")
    )


def carregar_entradas(usuario) -> list[Entrada]:  # noqa: ANN001
    return list(
        Entrada.objects.filter(usuario=usuario)
        .order_by("-data", "-criado_em")
        .select_related("fonte")
    )


# ---------------------------------------------------------------------------
# Abrir listagem — chamado pelo menu
# ---------------------------------------------------------------------------


def abrir_lista_gastos(sessao: SessaoConversa) -> str:
    usuario = _obter_usuario()
    if not usuario:
        return "❌ Usuário não configurado."

    gastos = carregar_gastos(usuario)
    if not gastos:
        _resetar(sessao)
        return "📭 Nenhum gasto registrado.\n\n" + MENU_TEXTO

    sessao.estado = "listando_gastos"
    sessao.dados_temporarios = {"pagina": 1}
    sessao.save()
    return montar_lista_gastos(gastos, 1, total_paginas_gastos(gastos))


def abrir_lista_entradas(sessao: SessaoConversa) -> str:
    usuario = _obter_usuario()
    if not usuario:
        return "❌ Usuário não configurado."

    entradas = carregar_entradas(usuario)
    if not entradas:
        _resetar(sessao)
        return "📭 Nenhuma entrada registrada.\n\n" + MENU_TEXTO

    sessao.estado = "listando_entradas"
    sessao.dados_temporarios = {"pagina": 1}
    sessao.save()
    return montar_lista_entradas(
        entradas, 1, total_paginas_entradas(entradas)
    )


# ---------------------------------------------------------------------------
# Dispatcher de estados CRUD
# ---------------------------------------------------------------------------


def processar_estado_crud(sessao: SessaoConversa, corpo: str) -> str:
    from whatsapp.services.handlers_edicao import (  # noqa: PLC0415
        processar_edicao,
    )
    from whatsapp.services.handlers_exclusao import (  # noqa: PLC0415
        processar_exclusao,
    )
    from whatsapp.services.handlers_listagem import (  # noqa: PLC0415
        processar_listagem,
    )

    estados_listagem = {"listando_gastos", "listando_entradas"}
    estados_exclusao = {
        "confirmando_exclusao_gasto",
        "confirmando_exclusao_entrada",
    }
    estados_edicao = {
        "editando_gasto_campo",
        "editando_gasto_valor",
        "editando_gasto_categoria",
        "editando_entrada_campo",
        "editando_entrada_valor",
        "editando_entrada_fonte",
    }

    if sessao.estado in estados_listagem:
        return processar_listagem(sessao, corpo)
    if sessao.estado in estados_exclusao:
        return processar_exclusao(sessao, corpo)
    if sessao.estado in estados_edicao:
        return processar_edicao(sessao, corpo)

    _resetar(sessao)
    return MENU_TEXTO
