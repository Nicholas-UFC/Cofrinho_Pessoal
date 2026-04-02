from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import pytest
from django.test import override_settings

from whatsapp.models import SessaoConversa
from whatsapp.services import processar_mensagem

CHAT_ID = "120363423218993414@g.us"
OWNER = "dono"

# ---------------------------------------------------------------------------
# Rate limit — proteção contra spam de mensagens simultâneas
# ---------------------------------------------------------------------------
#
# O bot implementa um rate limit para evitar que o usuário envie muitas
# mensagens em sequência muito rápida, o que poderia acontecer por engano
# (cola de mensagens atrasadas) ou intencionalmente.
#
# A regra: no máximo 3 mensagens dentro de uma janela deslizante de 5
# segundos. Na 4ª mensagem dentro desse período, o bot responde com um aviso
# listando todas as mensagens recebidas no período e pedindo que o usuário
# reenvie pausadamente — sem processar o comando.
#
# Após a janela expirar (mais de 5 segundos da primeira mensagem), o rate
# limit é zerado e o bot volta a funcionar normalmente.
#
# Para testar isso de forma determinística, os testes usam `patch` na função
# `_agora()` de `whatsapp.services`, controlando o timestamp de cada mensagem
# sem depender do relógio real. Isso torna os testes rápidos e previsíveis.
# ---------------------------------------------------------------------------

_AGORA = datetime(2026, 3, 27, 12, 0, 0, tzinfo=UTC)


def _enviar(corpo: str, delta_segundos: float = 0.0) -> str:
    momento = _AGORA + timedelta(seconds=delta_segundos)
    with patch("whatsapp.services.processador._agora", return_value=momento):
        return processar_mensagem(CHAT_ID, corpo)


# ---------------------------------------------------------------------------
# Dentro do limite — sem rate limit
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_tres_mensagens_rapidas_nao_ativam_rate_limit() -> None:
    _enviar("menu", 0)
    _enviar("menu", 1)
    resposta = _enviar("menu", 2)
    assert "Muitas mensagens" not in resposta


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_mensagens_espalhadas_nao_ativam_rate_limit() -> None:
    _enviar("menu", 0)
    _enviar("menu", 6)   # fora da janela de 5s
    resposta = _enviar("menu", 12)
    assert "Muitas mensagens" not in resposta


# ---------------------------------------------------------------------------
# Rate limit ativado
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_quarta_mensagem_rapida_ativa_rate_limit() -> None:
    _enviar("menu", 0)
    _enviar("menu", 1)
    _enviar("menu", 2)
    resposta = _enviar("menu", 3)
    assert "Muitas mensagens" in resposta


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_rate_limit_lista_todas_as_mensagens_do_periodo() -> None:
    _enviar("menu", 0)
    _enviar("1", 1)
    _enviar("25.50", 2)
    resposta = _enviar("2", 3)

    assert "menu" in resposta
    assert '"1"' in resposta
    assert '"25.50"' in resposta
    assert '"2"' in resposta


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_rate_limit_orienta_reenviar_pausadamente() -> None:
    _enviar("menu", 0)
    _enviar("1", 1)
    _enviar("25.50", 2)
    resposta = _enviar("2", 3)

    assert "pausadamente" in resposta.lower()


# ---------------------------------------------------------------------------
# Recuperação após janela expirar
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_apos_janela_expirar_volta_a_funcionar() -> None:
    _enviar("menu", 0)
    _enviar("menu", 1)
    _enviar("menu", 2)
    _enviar("menu", 3)   # rate limit

    # Após 6 segundos (fora da janela de 5s), deve funcionar novamente
    resposta = _enviar("menu", 9)
    assert "Muitas mensagens" not in resposta
    assert "Cofrinho Pessoal" in resposta


# ---------------------------------------------------------------------------
# Estado da sessão durante rate limit
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@override_settings(WAHA_OWNER_USERNAME=OWNER)
def test_rate_limit_nao_altera_estado_da_sessao() -> None:
    _enviar("1", 0)  # vai para aguardando_valor_gasto
    _enviar("abc", 1)  # valor inválido, estado não muda
    _enviar("abc", 2)  # valor inválido, estado não muda
    _enviar("abc", 3)  # rate limit

    sessao = SessaoConversa.objects.get(chat_id=CHAT_ID)
    # Estado deve continuar onde estava antes do rate limit
    assert sessao.estado == "aguardando_valor_gasto"
