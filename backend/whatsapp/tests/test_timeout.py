from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import pytest
from django.test import override_settings

from whatsapp.models import SessaoConversa
from whatsapp.services import processar_mensagem

CHAT_ID = "120363423218993414@g.us"
OWNER = "dono"

_AGORA = datetime(2026, 3, 27, 12, 0, 0, tzinfo=UTC)


def _enviar(corpo: str, delta_minutos: float = 0.0) -> str:
    momento = _AGORA + timedelta(minutes=delta_minutos)
    with patch("whatsapp.services._agora", return_value=momento):
        return processar_mensagem(CHAT_ID, corpo)


# ---------------------------------------------------------------------------
# Sem timeout — sessão ativa
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_sessao_ativa_nao_reseta() -> None:
    """Dentro do prazo, estado é preservado."""
    _enviar("1")  # entra em aguardando_valor_gasto
    _enviar("oi", delta_minutos=4.9)  # 4min59s — ainda válido
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "aguardando_valor_gasto"


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_estado_menu_nunca_expira() -> None:
    """Estado 'menu' não gera aviso de timeout."""
    _enviar("menu")
    resposta = _enviar("menu", delta_minutos=60)
    assert "expirada" not in resposta.lower()


# ---------------------------------------------------------------------------
# Com timeout — sessão expirada
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_timeout_reseta_estado() -> None:
    """Após 5 minutos, estado volta para menu."""
    _enviar("1")  # entra em aguardando_valor_gasto
    _enviar("oi", delta_minutos=5.1)  # 5min06s — expirado
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.estado == "menu"


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_timeout_avisa_usuario() -> None:
    """Mensagem de aviso é enviada ao expirar."""
    _enviar("1")
    resposta = _enviar("oi", delta_minutos=5.1)
    assert "expirada" in resposta.lower()
    assert "Cofrinho Pessoal" in resposta


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_timeout_limpa_dados_temporarios() -> None:
    """Dados temporários são apagados ao expirar."""
    _enviar("1")
    _enviar("25,00")  # salva valor nos dados_temporarios
    _enviar("oi", delta_minutos=5.1)
    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    assert sessao.dados_temporarios == {} or "valor" not in sessao.dados_temporarios


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_timeout_reseta_qualquer_estado_intermediario() -> None:
    """Timeout funciona em todos os estados intermediários."""
    estados_intermediarios = [
        ("1",    "aguardando_valor_gasto"),
        ("2",    "aguardando_valor_entrada"),
    ]
    for comando, estado_esperado in estados_intermediarios:
        SessaoConversa.objects.filter(chat_id=CHAT_ID).delete()
        _enviar(comando)
        sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
        assert sessao.estado == estado_esperado

        _enviar("oi", delta_minutos=5.1)
        sessao.refresh_from_db()
        assert sessao.estado == "menu"
