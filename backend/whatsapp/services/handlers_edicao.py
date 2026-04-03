import math
from decimal import Decimal

from financas.models import Categoria, Entrada, Fonte, Gasto
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
from whatsapp.services.utils import (
    MENU_TEXTO,
    _listar_categorias,
    _listar_fontes,
    _obter_usuario,
    _parse_valor,
    _resetar,
)

_MSG_CAMPO_GASTO = (
    "Digite *1* para valor, *2* para categoria, "
    "*v* para voltar ou *0* para sair."
)
_MSG_CAMPO_ENTRADA = (
    "Digite *1* para valor, *2* para fonte, *v* para voltar ou *0* para sair."
)
_MSG_CONFIRMACAO = (
    "Digite *s* para confirmar, *v* para voltar ou *0* para sair."
)


# ---------------------------------------------------------------------------
# Dispatcher de edição
# ---------------------------------------------------------------------------


def processar_edicao(sessao: SessaoConversa, corpo: str) -> str:
    despachantes = {
        "editando_gasto_campo": _processar_gasto_campo,
        "editando_gasto_valor": _processar_gasto_valor,
        "editando_gasto_categoria": _processar_gasto_categoria,
        "editando_entrada_campo": _processar_entrada_campo,
        "editando_entrada_valor": _processar_entrada_valor,
        "editando_entrada_fonte": _processar_entrada_fonte,
    }
    handler = despachantes.get(sessao.estado)
    if handler is None:
        _resetar(sessao)
        return MENU_TEXTO
    return handler(sessao, corpo)


# ---------------------------------------------------------------------------
# Helpers compartilhados
# ---------------------------------------------------------------------------


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


def _texto_campo_gasto(gasto: Gasto) -> str:
    data = gasto.data.strftime("%d/%m/%Y")
    criado = gasto.criado_em.strftime("%d/%m/%Y")
    editado = gasto.atualizado_em.strftime("%d/%m/%Y")
    return (
        "*Editando gasto*\n"
        f"Valor atual: R$ {fmt_valor(gasto.valor)}\n"
        f"Categoria: {gasto.categoria.nome}\n"
        f"Data: {data} · Criado: {criado} · Editado: {editado}\n\n"
        "1. valor   2. categoria\n"
        "v voltar · 0 sair"
    )


def _texto_campo_entrada(entrada: Entrada) -> str:
    data = entrada.data.strftime("%d/%m/%Y")
    criado = entrada.criado_em.strftime("%d/%m/%Y")
    editado = entrada.atualizado_em.strftime("%d/%m/%Y")
    return (
        "*Editando entrada*\n"
        f"Valor atual: R$ {fmt_valor(entrada.valor)}\n"
        f"Fonte: {entrada.fonte.nome}\n"
        f"Data: {data} · Criado: {criado} · Editado: {editado}\n\n"
        "1. valor   2. fonte\n"
        "v voltar · 0 sair"
    )


# ---------------------------------------------------------------------------
# Abrir edição a partir da lista
# ---------------------------------------------------------------------------


def iniciar_edicao_gasto(
    sessao: SessaoConversa,
    corpo: str,
    gastos: list[Gasto],
    pagina: int,
) -> str:
    inicio = (pagina - 1) * ITENS_POR_PAGINA
    fatia = gastos[inicio : inicio + ITENS_POR_PAGINA]
    sufixo = corpo[1:]
    try:
        idx = int(sufixo)
    except ValueError:
        idx = -1
    if idx < 1 or idx > len(fatia):
        total = math.ceil(len(gastos) / ITENS_POR_PAGINA)
        return "⚠️ Índice inválido.\n\n" + montar_lista_gastos(
            gastos, pagina, total
        )
    gasto = fatia[idx - 1]
    # Substitui dados_temporarios inteiramente para zerar mensagens_recentes
    # e evitar falso positivo de rate limit em fluxos multi-etapa.
    sessao.dados_temporarios = {"gasto_id": gasto.pk, "pagina": pagina}
    sessao.estado = "editando_gasto_campo"
    sessao.save()
    return _texto_campo_gasto(gasto)


def iniciar_edicao_entrada(
    sessao: SessaoConversa,
    corpo: str,
    entradas: list[Entrada],
    pagina: int,
) -> str:
    inicio = (pagina - 1) * ITENS_POR_PAGINA
    fatia = entradas[inicio : inicio + ITENS_POR_PAGINA]
    sufixo = corpo[1:]
    try:
        idx = int(sufixo)
    except ValueError:
        idx = -1
    if idx < 1 or idx > len(fatia):
        total = math.ceil(len(entradas) / ITENS_POR_PAGINA)
        return "⚠️ Índice inválido.\n\n" + montar_lista_entradas(
            entradas, pagina, total
        )
    entrada = fatia[idx - 1]
    sessao.dados_temporarios = {"entrada_id": entrada.pk, "pagina": pagina}
    sessao.estado = "editando_entrada_campo"
    sessao.save()
    return _texto_campo_entrada(entrada)


# ---------------------------------------------------------------------------
# Edição de gasto — escolha de campo
# ---------------------------------------------------------------------------


def _processar_gasto_campo(sessao: SessaoConversa, corpo: str) -> str:
    # Quando confirmando_campo está definido, estamos na confirmação.
    if sessao.dados_temporarios.get("confirmando_campo"):
        return _confirmar_edicao_gasto(sessao, corpo)
    if corpo == "0":
        _resetar(sessao)
        return MENU_TEXTO
    if corpo == "v":
        return _voltar_lista_gastos(sessao)
    gasto_id = sessao.dados_temporarios.get("gasto_id")
    try:
        gasto = Gasto.objects.select_related("categoria").get(pk=gasto_id)
    except Gasto.DoesNotExist:
        _resetar(sessao)
        return "❌ Gasto não encontrado.\n\n" + MENU_TEXTO
    return _escolher_campo_gasto(sessao, corpo, gasto)


def _escolher_campo_gasto(
    sessao: SessaoConversa, corpo: str, gasto: Gasto
) -> str:
    if corpo == "1":
        sessao.estado = "editando_gasto_valor"
        sessao.save()
        return (
            f"Valor atual: R$ {fmt_valor(gasto.valor)}\n"
            "Novo valor: (ex: 25,50 ou 1.500,00)\n"
            "v voltar · 0 sair"
        )
    if corpo == "2":
        usuario = _obter_usuario()
        if not usuario:
            return "❌ Usuário não configurado."
        lista = _listar_categorias(usuario)
        sessao.estado = "editando_gasto_categoria"
        sessao.save()
        return f"Nova categoria:\n\n{lista}\n\nv voltar · 0 sair"
    return _MSG_CAMPO_GASTO


def _confirmar_edicao_gasto(sessao: SessaoConversa, corpo: str) -> str:
    if corpo == "0":
        _resetar(sessao)
        return MENU_TEXTO
    if corpo == "v":
        # Limpa confirmação e volta para escolha de campo.
        gasto_id = sessao.dados_temporarios.get("gasto_id")
        pagina = sessao.dados_temporarios.get("pagina", 1)
        sessao.dados_temporarios = {"gasto_id": gasto_id, "pagina": pagina}
        sessao.save()
        try:
            gasto = Gasto.objects.select_related("categoria").get(pk=gasto_id)
        except Gasto.DoesNotExist:
            _resetar(sessao)
            return "❌ Gasto não encontrado.\n\n" + MENU_TEXTO
        return _texto_campo_gasto(gasto)
    if corpo in ("s", "sim"):
        return _aplicar_edicao_gasto(sessao)
    return _MSG_CONFIRMACAO


def _aplicar_edicao_gasto(sessao: SessaoConversa) -> str:
    gasto_id = sessao.dados_temporarios.get("gasto_id")
    campo = sessao.dados_temporarios.get("confirmando_campo")
    pagina = sessao.dados_temporarios.get("pagina", 1)
    try:
        gasto = Gasto.objects.select_related("categoria").get(pk=gasto_id)
    except Gasto.DoesNotExist:
        _resetar(sessao)
        return "❌ Gasto não encontrado.\n\n" + MENU_TEXTO

    if campo == "valor":
        gasto.valor = Decimal(sessao.dados_temporarios["novo_valor"])
        gasto.save()
    elif campo == "categoria":
        cat = Categoria.objects.get(
            pk=sessao.dados_temporarios["nova_categoria_id"]
        )
        gasto.categoria = cat
        gasto.save()

    sessao.estado = "listando_gastos"
    sessao.dados_temporarios = {"pagina": pagina}
    sessao.save()
    usuario = _obter_usuario()
    if not usuario:
        return "❌ Usuário não configurado."
    gastos = carregar_gastos(usuario)
    return "✅ Gasto atualizado!\n\n" + montar_lista_gastos(
        gastos, pagina, total_paginas_gastos(gastos)
    )


# ---------------------------------------------------------------------------
# Edição de gasto — novo valor
# ---------------------------------------------------------------------------


def _processar_gasto_valor(sessao: SessaoConversa, corpo: str) -> str:
    if corpo == "0":
        _resetar(sessao)
        return MENU_TEXTO
    if corpo == "v":
        gasto_id = sessao.dados_temporarios.get("gasto_id")
        sessao.estado = "editando_gasto_campo"
        sessao.save()
        try:
            gasto = Gasto.objects.select_related("categoria").get(pk=gasto_id)
        except Gasto.DoesNotExist:
            _resetar(sessao)
            return "❌ Gasto não encontrado.\n\n" + MENU_TEXTO
        return _texto_campo_gasto(gasto)

    valor = _parse_valor(corpo)
    if valor is None:
        return "⚠️ Valor inválido. (ex: 25,50 ou 1.500,00)\nv voltar · 0 sair"

    gasto_id = sessao.dados_temporarios.get("gasto_id")
    try:
        gasto = Gasto.objects.select_related("categoria").get(pk=gasto_id)
    except Gasto.DoesNotExist:
        _resetar(sessao)
        return "❌ Gasto não encontrado.\n\n" + MENU_TEXTO

    sessao.dados_temporarios["novo_valor"] = str(valor)
    sessao.dados_temporarios["confirmando_campo"] = "valor"
    sessao.estado = "editando_gasto_campo"
    sessao.save()
    return (
        "Confirma a edição?\n\n"
        f"R$ {fmt_valor(gasto.valor)} → R$ {fmt_valor(valor)}\n"
        f"Categoria: {gasto.categoria.nome}\n\n"
        "s confirmar · v voltar · 0 sair"
    )


# ---------------------------------------------------------------------------
# Edição de gasto — nova categoria
# ---------------------------------------------------------------------------


def _processar_gasto_categoria(sessao: SessaoConversa, corpo: str) -> str:
    if corpo == "0":
        _resetar(sessao)
        return MENU_TEXTO
    if corpo == "v":
        gasto_id = sessao.dados_temporarios.get("gasto_id")
        sessao.estado = "editando_gasto_campo"
        sessao.save()
        try:
            gasto = Gasto.objects.select_related("categoria").get(pk=gasto_id)
        except Gasto.DoesNotExist:
            _resetar(sessao)
            return "❌ Gasto não encontrado.\n\n" + MENU_TEXTO
        return _texto_campo_gasto(gasto)
    usuario = _obter_usuario()
    if not usuario:
        return "❌ Usuário não configurado."
    return _selecionar_categoria_gasto(sessao, corpo, usuario)


def _selecionar_categoria_gasto(
    sessao: SessaoConversa, corpo: str, usuario: object
) -> str:
    categorias = list(Categoria.objects.filter(usuario=usuario))
    try:
        idx = int(corpo) - 1
        if not 0 <= idx < len(categorias):
            raise ValueError
    except ValueError:
        lista = _listar_categorias(usuario)
        return f"⚠️ Opção inválida.\n\n{lista}\n\nv voltar · 0 sair"
    nova = categorias[idx]
    gasto_id = sessao.dados_temporarios.get("gasto_id")
    try:
        gasto = Gasto.objects.select_related("categoria").get(pk=gasto_id)
    except Gasto.DoesNotExist:
        _resetar(sessao)
        return "❌ Gasto não encontrado.\n\n" + MENU_TEXTO
    sessao.dados_temporarios["nova_categoria_id"] = nova.pk
    sessao.dados_temporarios["confirmando_campo"] = "categoria"
    sessao.estado = "editando_gasto_campo"
    sessao.save()
    return (
        "Confirma a edição?\n\n"
        f"Categoria: {gasto.categoria.nome} → {nova.nome}\n"
        f"Valor: R$ {fmt_valor(gasto.valor)}\n\n"
        "s confirmar · v voltar · 0 sair"
    )


# ---------------------------------------------------------------------------
# Edição de entrada — escolha de campo
# ---------------------------------------------------------------------------


def _processar_entrada_campo(sessao: SessaoConversa, corpo: str) -> str:
    if sessao.dados_temporarios.get("confirmando_campo"):
        return _confirmar_edicao_entrada(sessao, corpo)
    if corpo == "0":
        _resetar(sessao)
        return MENU_TEXTO
    if corpo == "v":
        return _voltar_lista_entradas(sessao)
    entrada_id = sessao.dados_temporarios.get("entrada_id")
    try:
        entrada = Entrada.objects.select_related("fonte").get(pk=entrada_id)
    except Entrada.DoesNotExist:
        _resetar(sessao)
        return "❌ Entrada não encontrada.\n\n" + MENU_TEXTO
    return _escolher_campo_entrada(sessao, corpo, entrada)


def _escolher_campo_entrada(
    sessao: SessaoConversa, corpo: str, entrada: Entrada
) -> str:
    if corpo == "1":
        sessao.estado = "editando_entrada_valor"
        sessao.save()
        return (
            f"Valor atual: R$ {fmt_valor(entrada.valor)}\n"
            "Novo valor: (ex: 3.000,00)\n"
            "v voltar · 0 sair"
        )
    if corpo == "2":
        usuario = _obter_usuario()
        if not usuario:
            return "❌ Usuário não configurado."
        lista = _listar_fontes(usuario)
        sessao.estado = "editando_entrada_fonte"
        sessao.save()
        return f"Nova fonte:\n\n{lista}\n\nv voltar · 0 sair"
    return _MSG_CAMPO_ENTRADA


def _confirmar_edicao_entrada(sessao: SessaoConversa, corpo: str) -> str:
    if corpo == "0":
        _resetar(sessao)
        return MENU_TEXTO
    if corpo == "v":
        entrada_id = sessao.dados_temporarios.get("entrada_id")
        pagina = sessao.dados_temporarios.get("pagina", 1)
        sessao.dados_temporarios = {"entrada_id": entrada_id, "pagina": pagina}
        sessao.save()
        try:
            entrada = Entrada.objects.select_related("fonte").get(
                pk=entrada_id
            )
        except Entrada.DoesNotExist:
            _resetar(sessao)
            return "❌ Entrada não encontrada.\n\n" + MENU_TEXTO
        return _texto_campo_entrada(entrada)
    if corpo in ("s", "sim"):
        return _aplicar_edicao_entrada(sessao)
    return _MSG_CONFIRMACAO


def _aplicar_edicao_entrada(sessao: SessaoConversa) -> str:
    entrada_id = sessao.dados_temporarios.get("entrada_id")
    campo = sessao.dados_temporarios.get("confirmando_campo")
    pagina = sessao.dados_temporarios.get("pagina", 1)
    try:
        entrada = Entrada.objects.select_related("fonte").get(pk=entrada_id)
    except Entrada.DoesNotExist:
        _resetar(sessao)
        return "❌ Entrada não encontrada.\n\n" + MENU_TEXTO

    if campo == "valor":
        entrada.valor = Decimal(sessao.dados_temporarios["novo_valor"])
        entrada.save()
    elif campo == "fonte":
        fonte = Fonte.objects.get(pk=sessao.dados_temporarios["nova_fonte_id"])
        entrada.fonte = fonte
        entrada.save()

    sessao.estado = "listando_entradas"
    sessao.dados_temporarios = {"pagina": pagina}
    sessao.save()
    usuario = _obter_usuario()
    if not usuario:
        return "❌ Usuário não configurado."
    entradas = carregar_entradas(usuario)
    return "✅ Entrada atualizada!\n\n" + montar_lista_entradas(
        entradas, pagina, total_paginas_entradas(entradas)
    )


# ---------------------------------------------------------------------------
# Edição de entrada — novo valor
# ---------------------------------------------------------------------------


def _processar_entrada_valor(sessao: SessaoConversa, corpo: str) -> str:
    if corpo == "0":
        _resetar(sessao)
        return MENU_TEXTO
    if corpo == "v":
        entrada_id = sessao.dados_temporarios.get("entrada_id")
        sessao.estado = "editando_entrada_campo"
        sessao.save()
        try:
            entrada = Entrada.objects.select_related("fonte").get(
                pk=entrada_id
            )
        except Entrada.DoesNotExist:
            _resetar(sessao)
            return "❌ Entrada não encontrada.\n\n" + MENU_TEXTO
        return _texto_campo_entrada(entrada)

    valor = _parse_valor(corpo)
    if valor is None:
        return "⚠️ Valor inválido. (ex: 3.000,00)\nv voltar · 0 sair"

    entrada_id = sessao.dados_temporarios.get("entrada_id")
    try:
        entrada = Entrada.objects.select_related("fonte").get(pk=entrada_id)
    except Entrada.DoesNotExist:
        _resetar(sessao)
        return "❌ Entrada não encontrada.\n\n" + MENU_TEXTO

    sessao.dados_temporarios["novo_valor"] = str(valor)
    sessao.dados_temporarios["confirmando_campo"] = "valor"
    sessao.estado = "editando_entrada_campo"
    sessao.save()
    return (
        "Confirma a edição?\n\n"
        f"R$ {fmt_valor(entrada.valor)} → R$ {fmt_valor(valor)}\n"
        f"Fonte: {entrada.fonte.nome}\n\n"
        "s confirmar · v voltar · 0 sair"
    )


# ---------------------------------------------------------------------------
# Edição de entrada — nova fonte
# ---------------------------------------------------------------------------


def _processar_entrada_fonte(sessao: SessaoConversa, corpo: str) -> str:
    if corpo == "0":
        _resetar(sessao)
        return MENU_TEXTO
    if corpo == "v":
        entrada_id = sessao.dados_temporarios.get("entrada_id")
        sessao.estado = "editando_entrada_campo"
        sessao.save()
        try:
            entrada = Entrada.objects.select_related("fonte").get(
                pk=entrada_id
            )
        except Entrada.DoesNotExist:
            _resetar(sessao)
            return "❌ Entrada não encontrada.\n\n" + MENU_TEXTO
        return _texto_campo_entrada(entrada)
    usuario = _obter_usuario()
    if not usuario:
        return "❌ Usuário não configurado."
    return _selecionar_fonte_entrada(sessao, corpo, usuario)


def _selecionar_fonte_entrada(
    sessao: SessaoConversa, corpo: str, usuario: object
) -> str:
    fontes = list(Fonte.objects.filter(usuario=usuario))
    try:
        idx = int(corpo) - 1
        if not 0 <= idx < len(fontes):
            raise ValueError
    except ValueError:
        lista = _listar_fontes(usuario)
        return f"⚠️ Opção inválida.\n\n{lista}\n\nv voltar · 0 sair"
    nova = fontes[idx]
    entrada_id = sessao.dados_temporarios.get("entrada_id")
    try:
        entrada = Entrada.objects.select_related("fonte").get(pk=entrada_id)
    except Entrada.DoesNotExist:
        _resetar(sessao)
        return "❌ Entrada não encontrada.\n\n" + MENU_TEXTO
    sessao.dados_temporarios["nova_fonte_id"] = nova.pk
    sessao.dados_temporarios["confirmando_campo"] = "fonte"
    sessao.estado = "editando_entrada_campo"
    sessao.save()
    return (
        "Confirma a edição?\n\n"
        f"Fonte: {entrada.fonte.nome} → {nova.nome}\n"
        f"Valor: R$ {fmt_valor(entrada.valor)}\n\n"
        "s confirmar · v voltar · 0 sair"
    )
