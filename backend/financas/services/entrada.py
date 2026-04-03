from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User

from financas.models import Entrada, Fonte


def criar_entrada(
    usuario: User,
    valor: Decimal,
    fonte: Fonte,
    descricao: str,
    data: date,
) -> Entrada:
    """Cria e persiste uma nova entrada para o usuário informado."""
    return Entrada.objects.create(
        usuario=usuario,
        valor=valor,
        fonte=fonte,
        descricao=descricao,
        data=data,
    )


def editar_entrada(entrada: Entrada, **campos: object) -> Entrada:
    """Aplica alterações parciais a uma entrada existente e salva.

    Apenas campos presentes em `campos` são modificados.
    Exemplo: editar_entrada(entrada, valor=Decimal("1500.00"))
    """
    for campo, valor in campos.items():
        setattr(entrada, campo, valor)
    entrada.save()
    return entrada
