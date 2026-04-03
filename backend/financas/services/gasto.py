from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User

from financas.models import Categoria, Gasto


def criar_gasto(
    usuario: User,
    valor: Decimal,
    categoria: Categoria,
    descricao: str,
    data: date,
) -> Gasto:
    """Cria e persiste um novo gasto para o usuário informado."""
    return Gasto.objects.create(
        usuario=usuario,
        valor=valor,
        categoria=categoria,
        descricao=descricao,
        data=data,
    )


def editar_gasto(gasto: Gasto, **campos: object) -> Gasto:
    """Aplica alterações parciais a um gasto existente e salva.

    Apenas campos presentes em `campos` são modificados.
    Exemplo: editar_gasto(gasto, valor=Decimal("50.00"))
    """
    for campo, valor in campos.items():
        setattr(gasto, campo, valor)
    gasto.save()
    return gasto
