import pytest


@pytest.fixture(autouse=True)
def desabilitar_api_key(settings: pytest.FixtureRequest) -> None:
    """Desabilita validação de API key para todos os testes de webhook.

    Os testes de autenticação (test_webhook_autenticacao.py) sobrescrevem
    explicitamente via @override_settings(WAHA_API_KEY=...).
    """
    settings.WAHA_API_KEY = ""
