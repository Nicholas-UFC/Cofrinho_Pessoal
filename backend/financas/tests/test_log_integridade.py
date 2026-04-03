import hashlib
import json

import pytest
from django.contrib.auth.models import User

from financas.models import LogAuditoria

# ---------------------------------------------------------------------------
# Integridade do LogAuditoria via SHA-256 — OWASP prática 130
#
# "Use a cryptographic hash function to validate log entry integrity."
# Verifica que o hash é gerado automaticamente e que alterações no
# conteúdo do log produzem hashes diferentes (detecção de adulteração).
# ---------------------------------------------------------------------------


@pytest.fixture
def usuario(db: None) -> User:
    return User.objects.create_user(
        username="audit_user", password="Senha@Forte12"
    )


@pytest.mark.django_db
def test_log_auditoria_gera_hash_automaticamente(usuario: User) -> None:
    log = LogAuditoria.objects.create(
        usuario=usuario,
        acao="criado",
        modelo="Gasto",
        objeto_id=1,
        detalhes={"valor": "100.00"},
    )
    assert log.hash_integridade != ""
    assert len(log.hash_integridade) == 64  # SHA-256 hex


@pytest.mark.django_db
def test_hash_corresponde_ao_conteudo(usuario: User) -> None:
    """O hash gerado deve ser reproduzível com os mesmos dados."""
    detalhes = {"valor": "50.00", "categoria": "Alimentação"}
    log = LogAuditoria.objects.create(
        usuario=usuario,
        acao="criado",
        modelo="Gasto",
        objeto_id=2,
        detalhes=detalhes,
    )

    conteudo_esperado = json.dumps(
        {
            "usuario_id": usuario.pk,
            "acao": "criado",
            "modelo": "Gasto",
            "objeto_id": 2,
            "detalhes": detalhes,
        },
        sort_keys=True,
        ensure_ascii=True,
    )
    hash_esperado = hashlib.sha256(conteudo_esperado.encode()).hexdigest()
    assert log.hash_integridade == hash_esperado


@pytest.mark.django_db
def test_logs_diferentes_geram_hashes_diferentes(usuario: User) -> None:
    log1 = LogAuditoria.objects.create(
        usuario=usuario,
        acao="criado",
        modelo="Gasto",
        objeto_id=10,
        detalhes={"valor": "10.00"},
    )
    log2 = LogAuditoria.objects.create(
        usuario=usuario,
        acao="deletado",
        modelo="Gasto",
        objeto_id=10,
        detalhes={"valor": "10.00"},
    )
    assert log1.hash_integridade != log2.hash_integridade


@pytest.mark.django_db
def test_hash_nao_muda_em_re_save(usuario: User) -> None:
    """Hash na criação não deve ser recalculado em saves posteriores."""
    log = LogAuditoria.objects.create(
        usuario=usuario,
        acao="criado",
        modelo="Categoria",
        objeto_id=5,
        detalhes={},
    )
    hash_original = log.hash_integridade

    log.save()

    log.refresh_from_db()
    assert log.hash_integridade == hash_original


@pytest.mark.django_db
def test_adulteracao_detectavel(usuario: User) -> None:
    """Se alguém alterar o hash no banco, é possível detectar a adulteração."""
    log = LogAuditoria.objects.create(
        usuario=usuario,
        acao="criado",
        modelo="Fonte",
        objeto_id=7,
        detalhes={"nome": "Salário"},
    )
    hash_original = log.hash_integridade

    # Simula adulteração direta no banco.
    LogAuditoria.objects.filter(pk=log.pk).update(hash_integridade="0" * 64)
    log.refresh_from_db()

    # O hash salvo difere do recalculado — adulteração detectada.
    assert log.hash_integridade != hash_original
    assert log._calcular_hash() == hash_original
