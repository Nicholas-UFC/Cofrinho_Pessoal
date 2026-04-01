import logging
from datetime import UTC, datetime, timedelta

from whatsapp.models import SessaoConversa
from whatsapp.services.handlers_entrada import (
    processar_confirmacao_entrada,
    processar_fonte_entrada,
    processar_valor_entrada,
)
from whatsapp.services.handlers_gasto import (
    processar_categoria_gasto,
    processar_confirmacao_gasto,
    processar_valor_gasto,
)
from whatsapp.services.utils import (
    COMANDOS_CONHECIDOS,
    MENU_TEXTO,
    _cancelar,
    _obter_resumo,
    _obter_usuario,
    _resetar,
)

logger = logging.getLogger(__name__)

# Prefixo invisível adicionado a todas as respostas do bot.
# Permite que o webhook ignore o echo do message.any sem depender de IDs.
PREFIXO_BOT = "\u200b"

_TRIGGER_MENU = ("menu",)

_JANELA_RATE_LIMIT = 5    # segundos
_MAX_MENSAGENS = 3         # mensagens permitidas na janela
_TIMEOUT_SESSAO = 5        # minutos sem resposta para resetar o estado


def _agora() -> datetime:
    return datetime.now(tz=UTC)


def _verificar_timeout(sessao: SessaoConversa) -> str | None:
    """Reseta o estado se a sessão ficou inativa além do timeout.

    Usa ultima_atividade de dados_temporarios (mockável) em vez de
    atualizado_em (definido pelo Django com tempo real).
    Retorna mensagem de aviso ou None se ainda dentro do prazo.
    """
    if sessao.estado == "menu":
        return None
    ultima = sessao.dados_temporarios.get("ultima_atividade")
    if ultima is None:
        return None
    limite = timedelta(minutes=_TIMEOUT_SESSAO)
    if _agora() - datetime.fromisoformat(ultima) < limite:
        return None
    sessao.estado = "menu"
    sessao.dados_temporarios = {}
    sessao.save()
    return (
        "⏱️ *Sessão expirada por inatividade.*\n\n"
        "Sua operação anterior foi cancelada.\n\n"
        + MENU_TEXTO
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
    sessao.dados_temporarios["ultima_atividade"] = agora.isoformat()
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


def _normalizar_corpo(corpo: str) -> str:
    """Limpa a mensagem: minúsculas e sem espaços internos ou externos."""
    return corpo.lower().replace(" ", "")


def _processar_menu(sessao: SessaoConversa, corpo: str) -> str:
    if corpo in _TRIGGER_MENU:
        return MENU_TEXTO
    if corpo == "1":
        sessao.estado = "aguardando_valor_gasto"
        sessao.save()
        return (
            "Qual o valor do gasto? (ex: 25,50 ou 1.500,00)\n"
            "Digite 0 para cancelar."
        )
    if corpo == "2":
        sessao.estado = "aguardando_valor_entrada"
        sessao.save()
        return (
            "Qual o valor da entrada? (ex: 3.000,00)\n"
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


def processar_mensagem(chat_id: str, corpo: str) -> str:
    sessao, _ = SessaoConversa.objects.get_or_create(chat_id=chat_id)
    corpo = _normalizar_corpo(corpo)

    timeout = _verificar_timeout(sessao)
    if timeout:
        return timeout

    rate_limit = _verificar_rate_limit(sessao, corpo)
    if rate_limit:
        return rate_limit

    despachantes = {
        "menu": _processar_menu,
        "aguardando_valor_gasto": processar_valor_gasto,
        "aguardando_categoria_gasto": processar_categoria_gasto,
        "confirmando_gasto": processar_confirmacao_gasto,
        "aguardando_valor_entrada": processar_valor_entrada,
        "aguardando_fonte_entrada": processar_fonte_entrada,
        "confirmando_entrada": processar_confirmacao_entrada,
    }
    handler = despachantes.get(sessao.estado)
    resposta = MENU_TEXTO if handler is None else handler(sessao, corpo)
    return PREFIXO_BOT + resposta
