import re
from datetime import date
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.contrib.auth.models import User

from financas.models import Categoria, Entrada, Fonte, Gasto
from whatsapp.models import SessaoConversa

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

# Aceita: inteiro (25), milhar com ponto (25.000, 1.000.000),
# decimal com vírgula (25,00), ou combinação (5.000,50).
# Ponto exige exatamente 3 dígitos após ele. Vírgula exige exatamente 2.
_REGEX_VALOR = re.compile(r"^\d{1,3}(\.\d{3})*(,\d{2})?$")


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


def _parse_valor(texto: str) -> Decimal | None:
    if not _REGEX_VALOR.match(texto):
        return None
    normalizado = texto.replace(".", "").replace(",", ".")
    try:
        valor = Decimal(normalizado).quantize(Decimal("0.01"))
    except InvalidOperation:
        return None
    return valor if valor > 0 else None


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
