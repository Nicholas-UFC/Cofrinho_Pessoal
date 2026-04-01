from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User

from financas.models import Entrada, Fonte
from whatsapp.models import SessaoConversa
from whatsapp.services.utils import (
    MENU_TEXTO,
    _cancelar,
    _escolher_item,
    _listar_fontes,
    _obter_usuario,
    _parse_valor,
    _resetar,
    _sem_cadastro,
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


def processar_valor_entrada(sessao: SessaoConversa, corpo: str) -> str:
    if corpo == "0":
        return _cancelar(sessao)

    valor = _parse_valor(corpo)
    if valor is None:
        return (
            "⚠️ Valor inválido. Digite um número positivo (ex: 3.000,00)\n"
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


def processar_fonte_entrada(sessao: SessaoConversa, corpo: str) -> str:
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


_CONFIRMACAO_VALIDA = ("s", "sim")
_CANCELAMENTO_VALIDO = ("n", "nao", "não")


def processar_confirmacao_entrada(sessao: SessaoConversa, corpo: str) -> str:
    if corpo in _CONFIRMACAO_VALIDA:
        usuario = _obter_usuario()
        if not usuario:
            return "❌ Usuário não configurado."
        _salvar_entrada(sessao, usuario)
        _resetar(sessao)
        return "✅ Entrada registrada com sucesso!\n\n" + MENU_TEXTO
    if corpo in _CANCELAMENTO_VALIDO:
        return _cancelar(sessao)
    return "Digite *s* para confirmar ou *n* para cancelar."
