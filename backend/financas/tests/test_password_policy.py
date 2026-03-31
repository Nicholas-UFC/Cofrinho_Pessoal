import pytest
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

# ---------------------------------------------------------------------------
# Política de senhas — OWASP práticas 38-39
#
# Verifica comprimento mínimo (12), complexidade (maiúscula, número,
# especial) e que senhas fracas são rejeitadas na criação de usuários.
# ---------------------------------------------------------------------------


def _validar(senha: str) -> list[str]:
    """Retorna lista de mensagens de erro; lista vazia = senha válida."""
    try:
        validate_password(senha)
        return []
    except ValidationError as exc:
        return list(exc.messages)


# --- Comprimento mínimo ---


def test_senha_com_11_chars_rejeitada() -> None:
    erros = _validar("Curta@123ab")
    assert erros, "Senha com 11 chars deveria ser rejeitada"


def test_senha_com_12_chars_aceita_se_complexa() -> None:
    erros = _validar("Valida@1234x")
    assert not erros, f"Senha válida foi rejeitada: {erros}"


# --- Complexidade: maiúscula ---


def test_senha_sem_maiuscula_rejeitada() -> None:
    erros = _validar("somente_minusc@123")
    assert any("maiúscula" in e for e in erros)


def test_senha_com_maiuscula_aceita() -> None:
    erros = _validar("ComMaiuscula@123")
    assert not erros, f"Senha válida foi rejeitada: {erros}"


# --- Complexidade: dígito ---


def test_senha_sem_digito_rejeitada() -> None:
    erros = _validar("SemNumero@aqui!")
    assert any("número" in e for e in erros)


def test_senha_com_digito_aceita() -> None:
    erros = _validar("Com1Digito@aqui")
    assert not erros, f"Senha válida foi rejeitada: {erros}"


# --- Complexidade: especial ---


def test_senha_sem_especial_rejeitada() -> None:
    erros = _validar("SemEspecial1234")
    assert any("especial" in e for e in erros)


def test_senha_com_especial_aceita() -> None:
    erros = _validar("Com@Especial123")
    assert not erros, f"Senha válida foi rejeitada: {erros}"


# --- Integração: criar usuário com senha fraca ---


@pytest.mark.django_db
def test_criar_usuario_com_senha_fraca_levanta_erro() -> None:
    with pytest.raises(ValidationError):
        validate_password("fraca")


@pytest.mark.django_db
def test_criar_usuario_com_senha_forte_passa() -> None:
    user = User(username="valido")
    validate_password("Forte@Senha123", user=user)


# --- Senhas comuns rejeitadas ---


def test_senha_comum_rejeitada() -> None:
    # "password123456" consta na lista de senhas comuns do Django.
    erros = _validar("password123456")
    assert erros, "Senha comum deveria ser rejeitada"
