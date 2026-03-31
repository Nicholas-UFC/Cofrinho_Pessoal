import pytest
from axes.models import AccessAttempt
from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.throttling import (
    AnonRateThrottle,
    SimpleRateThrottle,
    UserRateThrottle,
)
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

# ---------------------------------------------------------------------------
# Rate limiting — OWASP prática 94
#
# Verifica que a API retorna 429 quando o limite de requisições é excedido.
# Usa cache local para não depender de Redis em testes.
# ---------------------------------------------------------------------------

_THROTTLE_CLASSES = [AnonRateThrottle, UserRateThrottle]
_THROTTLE_RATES = {"anon": "20/min", "user": "200/min"}


@pytest.fixture(autouse=True)
def ativar_throttling() -> None:
    """Re-habilita throttling nas classes DRF para estes testes.

    settings.py desabilita throttling em modo teste (_MODO_TESTE) para evitar
    que chamadas acumuladas ao /api/token/ bloqueiem outros testes.

    DRF define APIView.throttle_classes na importação, então a forma
    confiável de reativar é patchear o atributo de classe diretamente.
    """
    orig_classes = APIView.throttle_classes
    orig_rates = SimpleRateThrottle.THROTTLE_RATES

    APIView.throttle_classes = _THROTTLE_CLASSES
    SimpleRateThrottle.THROTTLE_RATES = _THROTTLE_RATES

    yield

    APIView.throttle_classes = orig_classes
    SimpleRateThrottle.THROTTLE_RATES = orig_rates


@pytest.fixture(autouse=True)
def limpar_cache(db: None) -> None:
    cache.clear()
    AccessAttempt.objects.all().delete()
    yield
    cache.clear()
    AccessAttempt.objects.all().delete()


@pytest.fixture
def usuario(db: None) -> User:
    return User.objects.create_user(
        username="throttle_user", password="Senha@Forte12"
    )


@pytest.fixture
def cliente_autenticado(usuario: User) -> APIClient:
    client = APIClient()
    token = AccessToken.for_user(usuario)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.fixture
def cliente_anonimo() -> APIClient:
    return APIClient()


@pytest.mark.django_db
def test_usuario_autenticado_respeita_limite(
    cliente_autenticado: APIClient,
) -> None:
    """Após 200 requisições/min, retorna 429."""
    limite = 200
    for _ in range(limite):
        resp = cliente_autenticado.get("/api/financas/gastos/")
        assert resp.status_code != status.HTTP_429_TOO_MANY_REQUESTS

    resp = cliente_autenticado.get("/api/financas/gastos/")
    assert resp.status_code == status.HTTP_429_TOO_MANY_REQUESTS


@pytest.mark.django_db
@override_settings(AXES_ENABLED=False)
def test_usuario_anonimo_respeita_limite(
    cliente_anonimo: APIClient,
) -> None:
    """Após 20 requisições/min ao endpoint público, retorna 429.

    AnonRateThrottle age antes da permissão em endpoints públicos (token).
    Em endpoints autenticados, a permissão retorna 401 antes do throttle.
    """
    limite = 20
    for _ in range(limite):
        cliente_anonimo.post(
            "/api/token/", {"username": "x", "password": "y"}
        )

    resp = cliente_anonimo.post(
        "/api/token/", {"username": "x", "password": "y"}
    )
    assert resp.status_code == status.HTTP_429_TOO_MANY_REQUESTS


@pytest.mark.django_db
@override_settings(AXES_ENABLED=False)
def test_limite_anonimo_menor_que_autenticado(
    cliente_anonimo: APIClient,
    cliente_autenticado: APIClient,
) -> None:
    """Anônimo tem limite menor: após 20, retorna 429; auth ainda passa."""
    for _ in range(21):
        cliente_anonimo.post(
            "/api/token/", {"username": "x", "password": "y"}
        )

    resp_anonimo = cliente_anonimo.post(
        "/api/token/", {"username": "x", "password": "y"}
    )
    assert resp_anonimo.status_code == status.HTTP_429_TOO_MANY_REQUESTS

    resp_auth = cliente_autenticado.get("/api/financas/gastos/")
    assert resp_auth.status_code != status.HTTP_429_TOO_MANY_REQUESTS
