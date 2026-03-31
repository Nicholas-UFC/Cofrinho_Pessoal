import pytest
from django.test import Client

from financas.middleware import (
    _MAX_ENDPOINT,
    _MAX_USER_AGENT,
    _sanitizar_ascii,
)
from financas.models import LogAcesso

# ---------------------------------------------------------------------------
# Sanitização de logs — OWASP práticas 9, 116
#
# Verifica que user_agent e endpoint são truncados e que caracteres
# não-ASCII/perigosos são removidos antes de persistir no LogAcesso.
# ---------------------------------------------------------------------------


# --- Testes unitários da função _sanitizar_ascii ---


def test_sanitizar_remove_caracteres_nao_ascii() -> None:
    resultado = _sanitizar_ascii("texto\x00com\nnull", 100)
    assert "\x00" not in resultado
    assert "\n" not in resultado


def test_sanitizar_trunca_ao_limite() -> None:
    longo = "a" * 600
    resultado = _sanitizar_ascii(longo, _MAX_USER_AGENT)
    assert len(resultado) == _MAX_USER_AGENT


def test_sanitizar_preserva_ascii_valido() -> None:
    texto = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    resultado = _sanitizar_ascii(texto, _MAX_USER_AGENT)
    assert resultado == texto


def test_sanitizar_remove_emoji_e_unicode() -> None:
    texto = "agente 🤖 com unicode \u00e9"
    resultado = _sanitizar_ascii(texto, 100)
    assert "🤖" not in resultado
    assert "\u00e9" not in resultado


# --- Testes de integração: LogAcesso persiste valores sanitizados ---


@pytest.mark.django_db
def test_user_agent_gigante_truncado_no_log(client: Client) -> None:
    agente_gigante = "A" * 2000
    client.get("/api/financas/gastos/", HTTP_USER_AGENT=agente_gigante)

    log = LogAcesso.objects.filter(endpoint="/api/financas/gastos/").first()
    assert log is not None
    assert len(log.user_agent) <= _MAX_USER_AGENT


@pytest.mark.django_db
def test_endpoint_truncado_no_log(client: Client) -> None:
    # Gera endpoint com path muito longo (mas válido para o test client).
    endpoint_longo = "/api/" + "x" * 300
    client.get(endpoint_longo)

    log = LogAcesso.objects.filter(
        endpoint__startswith="/api/"
    ).order_by("-criado_em").first()
    assert log is None or len(log.endpoint) <= _MAX_ENDPOINT


@pytest.mark.django_db
def test_user_agent_com_nao_ascii_sanitizado(client: Client) -> None:
    agente_unicode = "Mozilla \u00e9\u00e0 5.0 \x00 null byte"
    client.get(
        "/api/financas/gastos/", HTTP_USER_AGENT=agente_unicode
    )

    log = LogAcesso.objects.filter(endpoint="/api/financas/gastos/").first()
    assert log is not None
    assert "\x00" not in log.user_agent
    assert "\u00e9" not in log.user_agent
