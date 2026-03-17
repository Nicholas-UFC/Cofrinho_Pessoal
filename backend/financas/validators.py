from decimal import Decimal

from django.core.exceptions import ValidationError


def validar_valor_positivo(valor: Decimal) -> None:
    if valor <= 0:
        raise ValidationError("Apenas valores positivos são permitidos.")
