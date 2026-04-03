import re
from decimal import Decimal

from django.core.exceptions import ValidationError

# Caracteres que indicam tentativa de injeção — OWASP práticas 14-16.
_REGEX_PERIGOSO = re.compile(r"[\x00\r\n\t\x1b]|(\.\./)|(\.\.[/\\])")


def validar_valor_positivo(valor: Decimal) -> None:
    if valor <= 0:
        raise ValidationError("Apenas valores positivos são permitidos.")


def validar_caracteres_seguros(valor: str) -> None:
    """Rejeita null bytes, quebras de linha e path traversal — OWASP 14-16."""
    if _REGEX_PERIGOSO.search(valor):
        raise ValidationError("O campo contém caracteres não permitidos.")


class ValidadorComplexidadeSenha:
    """Exige pelo menos 1 maiúscula, 1 dígito e 1 especial — OWASP 38."""

    _ESPECIAIS = re.compile(r"[!@#$%^&*()\-_=+\[\]{};:'\",.<>?/\\|`~]")

    def validate(self, password: str, _user: object = None) -> None:
        erros = []
        if not any(c.isupper() for c in password):
            erros.append("pelo menos uma letra maiúscula")
        if not any(c.isdigit() for c in password):
            erros.append("pelo menos um número")
        if not self._ESPECIAIS.search(password):
            erros.append("pelo menos um caractere especial (!@#$%^&*...)")
        if erros:
            raise ValidationError(
                f"A senha precisa conter: {', '.join(erros)}."
            )

    def get_help_text(self) -> str:
        return (
            "A senha deve conter pelo menos uma letra maiúscula, "
            "um número e um caractere especial."
        )
