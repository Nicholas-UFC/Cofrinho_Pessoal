import contextlib
import math

from financas.models import Entrada, Gasto
from whatsapp.models import SessaoConversa
from whatsapp.services.handlers_crud import (
    ITENS_POR_PAGINA,
    carregar_entradas,
    carregar_gastos,
    fmt_valor,
    montar_lista_entradas,
    montar_lista_gastos,
    total_paginas_entradas,
    total_paginas_gastos,
)
from whatsapp.services.utils import MENU_TEXTO, _obter_usuario, _resetar

_MSG_CONFIRMACAO = (
    "Digite *s* para confirmar, *v* para voltar ou *0* para sair."
)


def _resolver_indice(corpo: str, prefixo: str, total: int) -> int | None:
    sufixo = corpo[len(prefixo) :]
    try:
        idx = int(sufixo)
    except ValueError:
        return None
    return idx if 1 <= idx <= total else None


# ---------------------------------------------------------------------------
# Gastos
# ---------------------------------------------------------------------------


def iniciar_exclusao_gasto(
    sessao: SessaoConversa,
    corpo: str,
    gastos: list[Gasto],
    pagina: int,
) -> str:
    inicio = (pagina - 1) * ITENS_POR_PAGINA
    fatia = gastos[inicio : inicio + ITENS_POR_PAGINA]
    idx = _resolver_indice(corpo, "x", len(fatia))
    if idx is None:
        total = math.ceil(len(gastos) / ITENS_POR_PAGINA)
        return "⚠️ Índice inválido.\n\n" + montar_lista_gastos(
            gastos, pagina, total
        )
    gasto = fatia[idx - 1]
    sessao.dados_temporarios = {"gasto_id": gasto.pk, "pagina": pagina}
    sessao.estado = "confirmando_exclusao_gasto"
    sessao.save()
    return _texto_excluir_gasto(gasto)


def _texto_excluir_gasto(gasto: Gasto) -> str:
    data = gasto.data.strftime("%d/%m/%Y")
    criado = gasto.criado_em.strftime("%d/%m/%Y")
    editado = gasto.atualizado_em.strftime("%d/%m/%Y")
    return (
        "🗑️ Excluir este gasto?\n\n"
        f"R$ {fmt_valor(gasto.valor)} | {gasto.categoria.nome} | {data}\n"
        f"Criado: {criado} · Editado: {editado}\n\n"
        "s confirmar · v voltar · 0 sair"
    )


def _voltar_lista_gastos(sessao: SessaoConversa) -> str:
    pagina = sessao.dados_temporarios.get("pagina", 1)
    sessao.estado = "listando_gastos"
    sessao.dados_temporarios = {"pagina": pagina}
    sessao.save()
    usuario = _obter_usuario()
    if not usuario:
        return "❌ Usuário não configurado."
    gastos = carregar_gastos(usuario)
    return montar_lista_gastos(gastos, pagina, total_paginas_gastos(gastos))


def processar_exclusao(sessao: SessaoConversa, corpo: str) -> str:
    if sessao.estado == "confirmando_exclusao_gasto":
        return _processar_confirmacao_exclusao_gasto(sessao, corpo)
    return _processar_confirmacao_exclusao_entrada(sessao, corpo)


def _processar_confirmacao_exclusao_gasto(
    sessao: SessaoConversa, corpo: str
) -> str:
    if corpo == "0":
        _resetar(sessao)
        return MENU_TEXTO
    if corpo == "v":
        return _voltar_lista_gastos(sessao)
    if corpo in ("s", "sim"):
        gasto_id = sessao.dados_temporarios.get("gasto_id")
        pagina = sessao.dados_temporarios.get("pagina", 1)
        with contextlib.suppress(Gasto.DoesNotExist):
            Gasto.objects.get(pk=gasto_id).delete()
        sessao.estado = "listando_gastos"
        sessao.dados_temporarios = {"pagina": pagina}
        sessao.save()
        usuario = _obter_usuario()
        if not usuario:
            return "❌ Usuário não configurado."
        gastos = carregar_gastos(usuario)
        total = total_paginas_gastos(gastos)
        return "✅ Gasto excluído!\n\n" + montar_lista_gastos(
            gastos, pagina, total
        )
    return _MSG_CONFIRMACAO


# ---------------------------------------------------------------------------
# Entradas
# ---------------------------------------------------------------------------


def iniciar_exclusao_entrada(
    sessao: SessaoConversa,
    corpo: str,
    entradas: list[Entrada],
    pagina: int,
) -> str:
    inicio = (pagina - 1) * ITENS_POR_PAGINA
    fatia = entradas[inicio : inicio + ITENS_POR_PAGINA]
    idx = _resolver_indice(corpo, "x", len(fatia))
    if idx is None:
        total = math.ceil(len(entradas) / ITENS_POR_PAGINA)
        return "⚠️ Índice inválido.\n\n" + montar_lista_entradas(
            entradas, pagina, total
        )
    entrada = fatia[idx - 1]
    sessao.dados_temporarios = {"entrada_id": entrada.pk, "pagina": pagina}
    sessao.estado = "confirmando_exclusao_entrada"
    sessao.save()
    return _texto_excluir_entrada(entrada)


def _texto_excluir_entrada(entrada: Entrada) -> str:
    data = entrada.data.strftime("%d/%m/%Y")
    criado = entrada.criado_em.strftime("%d/%m/%Y")
    editado = entrada.atualizado_em.strftime("%d/%m/%Y")
    return (
        "🗑️ Excluir esta entrada?\n\n"
        f"R$ {fmt_valor(entrada.valor)} | {entrada.fonte.nome} | {data}\n"
        f"Criado: {criado} · Editado: {editado}\n\n"
        "s confirmar · v voltar · 0 sair"
    )


def _voltar_lista_entradas(sessao: SessaoConversa) -> str:
    pagina = sessao.dados_temporarios.get("pagina", 1)
    sessao.estado = "listando_entradas"
    sessao.dados_temporarios = {"pagina": pagina}
    sessao.save()
    usuario = _obter_usuario()
    if not usuario:
        return "❌ Usuário não configurado."
    entradas = carregar_entradas(usuario)
    return montar_lista_entradas(
        entradas, pagina, total_paginas_entradas(entradas)
    )


def _processar_confirmacao_exclusao_entrada(
    sessao: SessaoConversa, corpo: str
) -> str:
    if corpo == "0":
        _resetar(sessao)
        return MENU_TEXTO
    if corpo == "v":
        return _voltar_lista_entradas(sessao)
    if corpo in ("s", "sim"):
        entrada_id = sessao.dados_temporarios.get("entrada_id")
        pagina = sessao.dados_temporarios.get("pagina", 1)
        with contextlib.suppress(Entrada.DoesNotExist):
            Entrada.objects.get(pk=entrada_id).delete()
        sessao.estado = "listando_entradas"
        sessao.dados_temporarios = {"pagina": pagina}
        sessao.save()
        usuario = _obter_usuario()
        if not usuario:
            return "❌ Usuário não configurado."
        entradas = carregar_entradas(usuario)
        total = total_paginas_entradas(entradas)
        return "✅ Entrada excluída!\n\n" + montar_lista_entradas(
            entradas, pagina, total
        )
    return _MSG_CONFIRMACAO
