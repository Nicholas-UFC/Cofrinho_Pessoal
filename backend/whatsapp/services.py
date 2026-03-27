from datetime import UTC, date, datetime, timedelta
from decimal import Decimal, InvalidOperation

import httpx
from django.conf import settings
from django.contrib.auth.models import User

from financas.models import Categoria, Entrada, Fonte, Gasto
from whatsapp.models import SessaoConversa

# Prefixo invisível adicionado a todas as respostas do bot.
# Permite que o webhook ignore o echo do message.any sem depender de IDs.
PREFIXO_BOT = "\u200b"

MENU_TEXTO = (
    "🤖 *Cofrinho Pessoal*\n\n"
    "O que você quer fazer?\n\n"
    "1️⃣ Registrar gasto\n"
    "2️⃣ Registrar entrada\n"
    "3️⃣ Ver resumo do mês\n\n"
    "Digite o número da opção."
)

COMANDOS_CONHECIDOS = (
    "📋 *Comandos disponíveis:*\n\n"
    "• *menu* — Exibe o menu principal\n"
    "• *1* — Registrar gasto (dentro do menu)\n"
    "• *2* — Registrar entrada (dentro do menu)\n"
    "• *3* — Ver resumo do mês (dentro do menu)\n"
    "• *0* — Cancelar operação em andamento\n"
    "• *s* / *n* — Confirmar ou cancelar"
)

_CONFIRMACAO_VALIDA = ("s", "sim")
_CANCELAMENTO_VALIDO = ("n", "nao", "não")
_TRIGGER_MENU = ("menu",)

_JANELA_RATE_LIMIT = 5   # segundos
_MAX_MENSAGENS = 3        # mensagens permitidas na janela


def _agora() -> datetime:
    return datetime.now(tz=UTC)


# ---------------------------------------------------------------------------
# Utilitários internos
# ---------------------------------------------------------------------------


def _obter_usuario() -> User | None:
    username = getattr(settings, "WAHA_OWNER_USERNAME", "")
    if not username:
        return None
    return User.objects.filter(username=username).first()


def _listar_categorias(usuario: User) -> str:
    categorias = Categoria.objects.filter(usuario=usuario)
    return "\n".join(
        f"{i + 1}. {c.nome}" for i, c in enumerate(categorias)
    )


def _listar_fontes(usuario: User) -> str:
    fontes = Fonte.objects.filter(usuario=usuario)
    return "\n".join(
        f"{i + 1}. {f.nome}" for i, f in enumerate(fontes)
    )


def _obter_resumo(usuario: User) -> str:
    hoje = date.today()
    gastos = Gasto.objects.filter(
        usuario=usuario, data__year=hoje.year, data__month=hoje.month
    )
    entradas = Entrada.objects.filter(
        usuario=usuario, data__year=hoje.year, data__month=hoje.month
    )
    total_gastos = sum((g.valor for g in gastos), Decimal("0"))
    total_entradas = sum((e.valor for e in entradas), Decimal("0"))
    saldo = total_entradas - total_gastos
    mes_ano = hoje.strftime("%m/%Y")
    return (
        f"📊 *Resumo de {mes_ano}*\n\n"
        f"💸 *Gastos:* R$ {total_gastos:.2f}\n"
        f"💰 *Entradas:* R$ {total_entradas:.2f}\n"
        f"📈 *Saldo:* R$ {saldo:.2f}"
    )


def _verificar_rate_limit(
    sessao: SessaoConversa, corpo: str
) -> str | None:
    """Retorna mensagem de rate limit se muitas mensagens chegaram rápido."""
    agora = _agora()
    janela_inicio = agora - timedelta(seconds=_JANELA_RATE_LIMIT)

    recentes = sessao.dados_temporarios.get("mensagens_recentes", [])
    recentes = [
        m for m in recentes
        if datetime.fromisoformat(m["ts"]) > janela_inicio
    ]
    recentes.append({"ts": agora.isoformat(), "corpo": corpo})

    sessao.dados_temporarios["mensagens_recentes"] = recentes
    sessao.save()

    if len(recentes) <= _MAX_MENSAGENS:
        return None

    lista = "\n".join(f'• "{m["corpo"]}"' for m in recentes)
    return (
        "⚠️ *Muitas mensagens ao mesmo tempo!*\n\n"
        "O sistema não consegue processar tantas mensagens "
        "simultâneas. Reenvie-as pausadamente.\n\n"
        "*Mensagens recebidas neste período:*\n"
        + lista
    )


def _parse_valor(texto: str) -> Decimal | None:
    try:
        valor = Decimal(texto.replace(",", "."))
        return valor if valor > 0 else None
    except InvalidOperation:
        return None


# ---------------------------------------------------------------------------
# Dispatcher principal
# ---------------------------------------------------------------------------


def _normalizar_corpo(corpo: str) -> str:
    """Limpa a mensagem: minúsculas e sem espaços internos ou externos."""
    return corpo.lower().replace(" ", "")


def processar_mensagem(chat_id: str, corpo: str) -> str:
    sessao, _ = SessaoConversa.objects.get_or_create(chat_id=chat_id)
    corpo = _normalizar_corpo(corpo)

    rate_limit = _verificar_rate_limit(sessao, corpo)
    if rate_limit:
        return rate_limit

    despachantes = {
        "menu": _processar_menu,
        "aguardando_valor_gasto": _processar_valor_gasto,
        "aguardando_categoria_gasto": _processar_categoria_gasto,
        "confirmando_gasto": _processar_confirmacao_gasto,
        "aguardando_valor_entrada": _processar_valor_entrada,
        "aguardando_fonte_entrada": _processar_fonte_entrada,
        "confirmando_entrada": _processar_confirmacao_entrada,
    }
    handler = despachantes.get(sessao.estado)
    resposta = MENU_TEXTO if handler is None else handler(sessao, corpo)
    return PREFIXO_BOT + resposta


# ---------------------------------------------------------------------------
# Handlers de estado
# ---------------------------------------------------------------------------


def _processar_menu(sessao: SessaoConversa, corpo: str) -> str:
    corpo_lower = corpo.lower()
    if corpo_lower in _TRIGGER_MENU:
        return MENU_TEXTO
    if corpo == "1":
        sessao.estado = "aguardando_valor_gasto"
        sessao.save()
        return "Qual o valor do gasto? (ex: 25.50)\nDigite 0 para cancelar."
    if corpo == "2":
        sessao.estado = "aguardando_valor_entrada"
        sessao.save()
        return (
            "Qual o valor da entrada? (ex: 3000.00)\n"
            "Digite 0 para cancelar."
        )
    if corpo == "3":
        usuario = _obter_usuario()
        if not usuario:
            return "❌ Usuário não configurado."
        return _obter_resumo(usuario)
    return (
        f"❓ Não conheço o comando *{corpo}*.\n\n"
        + COMANDOS_CONHECIDOS
    )


def _processar_valor_gasto(sessao: SessaoConversa, corpo: str) -> str:
    if corpo == "0":
        return _cancelar(sessao)

    valor = _parse_valor(corpo)
    if valor is None:
        return (
            "⚠️ Valor inválido. Digite um número positivo (ex: 25.50)\n"
            "Digite 0 para cancelar."
        )

    usuario = _obter_usuario()
    if not usuario:
        return "❌ Usuário não configurado."

    lista = _listar_categorias(usuario)
    if not lista:
        return _sem_cadastro(sessao, "categoria")

    sessao.dados_temporarios = {"valor": str(valor)}
    sessao.estado = "aguardando_categoria_gasto"
    sessao.save()
    return (
        f"Qual a categoria?\n\n{lista}\n\n"
        "Digite o número ou 0 para cancelar."
    )


def _processar_categoria_gasto(
    sessao: SessaoConversa, corpo: str
) -> str:
    if corpo == "0":
        return _cancelar(sessao)

    usuario = _obter_usuario()
    if not usuario:
        return "❌ Usuário não configurado."

    categorias = list(Categoria.objects.filter(usuario=usuario))
    categoria = _escolher_item(categorias, corpo)
    if categoria is None:
        lista = _listar_categorias(usuario)
        return (
            f"⚠️ Opção inválida.\n\n{lista}\n\n"
            "Digite o número ou 0 para cancelar."
        )

    sessao.dados_temporarios.update(
        {"categoria_id": categoria.pk, "categoria_nome": categoria.nome}
    )
    sessao.estado = "confirmando_gasto"
    sessao.save()
    return _texto_confirmacao_gasto(sessao)


def _processar_confirmacao_gasto(
    sessao: SessaoConversa, corpo: str
) -> str:
    corpo_lower = corpo.lower()
    if corpo_lower in _CONFIRMACAO_VALIDA:
        usuario = _obter_usuario()
        if not usuario:
            return "❌ Usuário não configurado."
        _salvar_gasto(sessao, usuario)
        _resetar(sessao)
        return "✅ Gasto registrado com sucesso!\n\n" + MENU_TEXTO
    if corpo_lower in _CANCELAMENTO_VALIDO:
        return _cancelar(sessao)
    return "Digite *s* para confirmar ou *n* para cancelar."


def _processar_valor_entrada(sessao: SessaoConversa, corpo: str) -> str:
    if corpo == "0":
        return _cancelar(sessao)

    valor = _parse_valor(corpo)
    if valor is None:
        return (
            "⚠️ Valor inválido. Digite um número positivo (ex: 3000.00)\n"
            "Digite 0 para cancelar."
        )

    usuario = _obter_usuario()
    if not usuario:
        return "❌ Usuário não configurado."

    lista = _listar_fontes(usuario)
    if not lista:
        return _sem_cadastro(sessao, "fonte")

    sessao.dados_temporarios = {"valor": str(valor)}
    sessao.estado = "aguardando_fonte_entrada"
    sessao.save()
    return f"Qual a fonte?\n\n{lista}\n\nDigite o número ou 0 para cancelar."


def _processar_fonte_entrada(sessao: SessaoConversa, corpo: str) -> str:
    if corpo == "0":
        return _cancelar(sessao)

    usuario = _obter_usuario()
    if not usuario:
        return "❌ Usuário não configurado."

    fontes = list(Fonte.objects.filter(usuario=usuario))
    fonte = _escolher_item(fontes, corpo)
    if fonte is None:
        lista = _listar_fontes(usuario)
        return (
            f"⚠️ Opção inválida.\n\n{lista}\n\n"
            "Digite o número ou 0 para cancelar."
        )

    sessao.dados_temporarios.update(
        {"fonte_id": fonte.pk, "fonte_nome": fonte.nome}
    )
    sessao.estado = "confirmando_entrada"
    sessao.save()
    return _texto_confirmacao_entrada(sessao)


def _processar_confirmacao_entrada(
    sessao: SessaoConversa, corpo: str
) -> str:
    corpo_lower = corpo.lower()
    if corpo_lower in _CONFIRMACAO_VALIDA:
        usuario = _obter_usuario()
        if not usuario:
            return "❌ Usuário não configurado."
        _salvar_entrada(sessao, usuario)
        _resetar(sessao)
        return "✅ Entrada registrada com sucesso!\n\n" + MENU_TEXTO
    if corpo_lower in _CANCELAMENTO_VALIDO:
        return _cancelar(sessao)
    return "Digite *s* para confirmar ou *n* para cancelar."


# ---------------------------------------------------------------------------
# Helpers de estado e persistência
# ---------------------------------------------------------------------------


def _cancelar(sessao: SessaoConversa) -> str:
    _resetar(sessao)
    return "❌ Cancelado.\n\n" + MENU_TEXTO


def _resetar(sessao: SessaoConversa) -> None:
    sessao.estado = "menu"
    sessao.dados_temporarios = {}
    sessao.save()


def _sem_cadastro(sessao: SessaoConversa, tipo: str) -> str:
    _resetar(sessao)
    return (
        f"❌ Nenhuma {tipo} cadastrada. "
        "Acesse o app para criar uma.\n\n" + MENU_TEXTO
    )


def _escolher_item(
    itens: list, corpo: str
) -> Categoria | Fonte | None:
    try:
        idx = int(corpo) - 1
        if 0 <= idx < len(itens):
            return itens[idx]
    except ValueError:
        pass
    return None


def _texto_confirmacao_gasto(sessao: SessaoConversa) -> str:
    valor = sessao.dados_temporarios["valor"]
    nome = sessao.dados_temporarios["categoria_nome"]
    return (
        "✅ Confirma o gasto?\n\n"
        f"*Valor:* R$ {valor}\n"
        f"*Categoria:* {nome}\n\n"
        "Digite *s* para confirmar ou *n* para cancelar."
    )


def _texto_confirmacao_entrada(sessao: SessaoConversa) -> str:
    valor = sessao.dados_temporarios["valor"]
    nome = sessao.dados_temporarios["fonte_nome"]
    return (
        "✅ Confirma a entrada?\n\n"
        f"*Valor:* R$ {valor}\n"
        f"*Fonte:* {nome}\n\n"
        "Digite *s* para confirmar ou *n* para cancelar."
    )


def _salvar_gasto(sessao: SessaoConversa, usuario: User) -> None:
    valor = Decimal(sessao.dados_temporarios["valor"])
    categoria = Categoria.objects.get(
        pk=sessao.dados_temporarios["categoria_id"]
    )
    Gasto.objects.create(
        usuario=usuario,
        descricao=f"Via WhatsApp - {categoria.nome}",
        valor=valor,
        categoria=categoria,
        data=date.today(),
    )


def _salvar_entrada(sessao: SessaoConversa, usuario: User) -> None:
    valor = Decimal(sessao.dados_temporarios["valor"])
    fonte = Fonte.objects.get(pk=sessao.dados_temporarios["fonte_id"])
    Entrada.objects.create(
        usuario=usuario,
        descricao=f"Via WhatsApp - {fonte.nome}",
        valor=valor,
        fonte=fonte,
        data=date.today(),
    )


# ---------------------------------------------------------------------------
# Cliente WAHA
# ---------------------------------------------------------------------------

# IDs das mensagens enviadas pelo bot — usados para ignorar o echo do message.any
_ids_enviados: set[str] = set()
_MAX_IDS_ENVIADOS = 200


def ids_enviados_pelo_bot() -> set[str]:
    return _ids_enviados


def _registrar_id_enviado(resposta: httpx.Response) -> None:
    try:
        msg_id = resposta.json().get("id")
    except Exception:
        return
    if not msg_id:
        return
    _ids_enviados.add(msg_id)
    if len(_ids_enviados) > _MAX_IDS_ENVIADOS:
        _ids_enviados.discard(next(iter(_ids_enviados)))


def enviar_mensagem(chat_id: str, texto: str) -> None:
    url = f"{settings.WAHA_API_URL}/api/sendText"
    headers = {"X-Api-Key": settings.WAHA_API_KEY}
    payload = {
        "chatId": chat_id,
        "text": texto,
        "session": getattr(settings, "WAHA_SESSION", "default"),
    }
    resposta = httpx.post(url, json=payload, headers=headers, timeout=10)
    _registrar_id_enviado(resposta)
