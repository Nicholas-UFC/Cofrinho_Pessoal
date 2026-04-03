from whatsapp.models import SessaoConversa
from whatsapp.services.handlers_crud import (
    carregar_entradas,
    carregar_gastos,
    montar_lista_entradas,
    montar_lista_gastos,
    total_paginas_entradas,
    total_paginas_gastos,
)
from whatsapp.services.handlers_edicao import (
    iniciar_edicao_entrada,
    iniciar_edicao_gasto,
)
from whatsapp.services.handlers_exclusao import (
    iniciar_exclusao_entrada,
    iniciar_exclusao_gasto,
)
from whatsapp.services.utils import MENU_TEXTO, _obter_usuario, _resetar


def processar_listagem(sessao: SessaoConversa, corpo: str) -> str:
    if sessao.estado == "listando_gastos":
        return _processar_listando_gastos(sessao, corpo)
    return _processar_listando_entradas(sessao, corpo)


def _paginar_gastos(
    sessao: SessaoConversa,
    corpo: str,
    gastos: list,
    pagina: int,
    total: int,
) -> str | None:
    if corpo == "p":
        if pagina >= total:
            return (
                "⚠️ Você já está na última página.\n\n"
                + montar_lista_gastos(gastos, pagina, total)
            )
        pagina += 1
        sessao.dados_temporarios["pagina"] = pagina
        sessao.save()
        return montar_lista_gastos(gastos, pagina, total)
    if corpo == "a":
        if pagina <= 1:
            return (
                "⚠️ Você já está na primeira página.\n\n"
                + montar_lista_gastos(gastos, pagina, total)
            )
        pagina -= 1
        sessao.dados_temporarios["pagina"] = pagina
        sessao.save()
        return montar_lista_gastos(gastos, pagina, total)
    return None


def _processar_listando_gastos(sessao: SessaoConversa, corpo: str) -> str:
    if corpo == "0":
        _resetar(sessao)
        return MENU_TEXTO
    usuario = _obter_usuario()
    if not usuario:
        return "❌ Usuário não configurado."
    gastos = carregar_gastos(usuario)
    total = total_paginas_gastos(gastos)
    pagina = sessao.dados_temporarios.get("pagina", 1)
    paginado = _paginar_gastos(sessao, corpo, gastos, pagina, total)
    if paginado is not None:
        return paginado
    if corpo.startswith("x"):
        return iniciar_exclusao_gasto(sessao, corpo, gastos, pagina)
    if corpo.startswith("e"):
        return iniciar_edicao_gasto(sessao, corpo, gastos, pagina)
    return "❓ Comando não reconhecido.\n\n" + montar_lista_gastos(
        gastos, pagina, total
    )


def _paginar_entradas(
    sessao: SessaoConversa,
    corpo: str,
    entradas: list,
    pagina: int,
    total: int,
) -> str | None:
    if corpo == "p":
        if pagina >= total:
            return (
                "⚠️ Você já está na última página.\n\n"
                + montar_lista_entradas(entradas, pagina, total)
            )
        pagina += 1
        sessao.dados_temporarios["pagina"] = pagina
        sessao.save()
        return montar_lista_entradas(entradas, pagina, total)
    if corpo == "a":
        if pagina <= 1:
            return (
                "⚠️ Você já está na primeira página.\n\n"
                + montar_lista_entradas(entradas, pagina, total)
            )
        pagina -= 1
        sessao.dados_temporarios["pagina"] = pagina
        sessao.save()
        return montar_lista_entradas(entradas, pagina, total)
    return None


def _processar_listando_entradas(sessao: SessaoConversa, corpo: str) -> str:
    if corpo == "0":
        _resetar(sessao)
        return MENU_TEXTO
    usuario = _obter_usuario()
    if not usuario:
        return "❌ Usuário não configurado."
    entradas = carregar_entradas(usuario)
    total = total_paginas_entradas(entradas)
    pagina = sessao.dados_temporarios.get("pagina", 1)
    paginado = _paginar_entradas(sessao, corpo, entradas, pagina, total)
    if paginado is not None:
        return paginado
    if corpo.startswith("x"):
        return iniciar_exclusao_entrada(sessao, corpo, entradas, pagina)
    if corpo.startswith("e"):
        return iniciar_edicao_entrada(sessao, corpo, entradas, pagina)
    return "❓ Comando não reconhecido.\n\n" + montar_lista_entradas(
        entradas, pagina, total
    )
