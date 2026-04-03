from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User

from financas.models import Categoria, Gasto
from whatsapp.models import SessaoConversa
from whatsapp.services.utils import (
    MENU_TEXTO,
    _cancelar,
    _escolher_item,
    _listar_categorias,
    _obter_usuario,
    _parse_valor,
    _resetar,
    _sem_cadastro,
)


def _texto_confirmacao_gasto(sessao: SessaoConversa) -> str:
    valor = sessao.dados_temporarios["valor"]
    nome = sessao.dados_temporarios["categoria_nome"]
    return (
        "✅ Confirma o gasto?\n\n"
        f"*Valor:* R$ {valor}\n"
        f"*Categoria:* {nome}\n\n"
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


def processar_valor_gasto(sessao: SessaoConversa, corpo: str) -> str:
    if corpo == "0":
        return _cancelar(sessao)

    valor = _parse_valor(corpo)
    if valor is None:
        return (
            "⚠️ Valor inválido. Digite um número positivo "
            "(ex: 25,50 ou 1.500,00)\n"
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
        f"Qual a categoria?\n\n{lista}\n\nDigite o número ou 0 para cancelar."
    )


def processar_categoria_gasto(sessao: SessaoConversa, corpo: str) -> str:
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


_CONFIRMACAO_VALIDA = ("s", "sim")
_CANCELAMENTO_VALIDO = ("n", "nao", "não")


def processar_confirmacao_gasto(sessao: SessaoConversa, corpo: str) -> str:
    if corpo in _CONFIRMACAO_VALIDA:
        usuario = _obter_usuario()
        if not usuario:
            return "❌ Usuário não configurado."
        _salvar_gasto(sessao, usuario)
        _resetar(sessao)
        return "✅ Gasto registrado com sucesso!\n\n" + MENU_TEXTO
    if corpo in _CANCELAMENTO_VALIDO:
        return _cancelar(sessao)
    return "Digite *s* para confirmar ou *n* para cancelar."
