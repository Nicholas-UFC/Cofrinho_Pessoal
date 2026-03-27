from decimal import Decimal

import pytest

from whatsapp.services import _parse_valor


# ---------------------------------------------------------------------------
# Formatos válidos
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("entrada,esperado", [
    ("25",              Decimal("25.00")),
    ("25,00",           Decimal("25.00")),
    ("25,50",           Decimal("25.50")),
    ("100,99",          Decimal("100.99")),
    ("25.000",          Decimal("25000.00")),
    ("250.000",         Decimal("250000.00")),
    ("1.000.000",       Decimal("1000000.00")),
    ("5.000,50",        Decimal("5000.50")),
    ("1.000.000,00",    Decimal("1000000.00")),
    ("999",             Decimal("999.00")),
    ("1.000",           Decimal("1000.00")),
])
def test_parse_valor_formatos_validos(entrada: str, esperado: Decimal) -> None:
    assert _parse_valor(entrada) == esperado


# ---------------------------------------------------------------------------
# Formatos inválidos
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("entrada", [
    "25.00",        # ponto com 2 dígitos (não é milhar)
    "25.0",         # ponto com 1 dígito
    "25.0000",      # ponto com 4 dígitos
    "25.000.0",     # último grupo do ponto tem 1 dígito
    "25,5",         # vírgula com 1 dígito
    "25,123",       # vírgula com 3 dígitos
    "abc",          # texto
    "",             # vazio
    "0",            # zero não é positivo
    "0,00",         # zero com vírgula
    "-25,00",       # negativo
    "25.000.00",    # segundo grupo do ponto tem 2 dígitos
])
def test_parse_valor_formatos_invalidos(entrada: str) -> None:
    assert _parse_valor(entrada) is None
