from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth.models import User

from financas.models import Categoria, Entrada, Fonte, Gasto, LogAuditoria

# ---------------------------------------------------------------------------
# Signals de auditoria — Gasto e Entrada
# ---------------------------------------------------------------------------
#
# O projeto usa Django signals (post_save, post_delete) para registrar
# automaticamente no LogAuditoria toda criação, atualização e deleção de
# registros financeiros. Esses signals são conectados nos apps via `apps.py`.
#
# Este arquivo cobre os dois modelos financeiros principais: Gasto e Entrada.
# São os modelos de maior volume de operações — e, por isso, os mais críticos
# para a rastreabilidade financeira do usuário.
#
# O que é verificado:
# — Criação: o signal gera um log com acao="criado" vinculado ao objeto correto.
# — Atualização: salvar com `.save()` gera acao="atualizado".
# — Deleção: deletar o objeto gera acao="deletado", preservando o
#   objeto_id no log mesmo depois que o registro sumiu do banco.
#
# Signals de Categoria, Fonte e User estão em
# `test_signals_categoria_fonte_user.py`.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def user(db: None) -> User:
    return User.objects.create_user(username="testuser", password="pass123")


@pytest.fixture
def categoria(user: User) -> Categoria:
    return Categoria.objects.create(nome="Alimentação", usuario=user)


@pytest.fixture
def fonte(user: User) -> Fonte:
    return Fonte.objects.create(nome="Salário", usuario=user)


# ---------------------------------------------------------------------------
# Gasto
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_criacao_gasto_gera_log(user: User, categoria: Categoria) -> None:
    gasto = Gasto.objects.create(
        usuario=user,
        descricao="Almoço",
        valor=Decimal("25.00"),
        categoria=categoria,
        data=date.today(),
    )

    log = LogAuditoria.objects.get(modelo="Gasto", objeto_id=gasto.pk)
    assert log.acao == "criado"
    assert log.usuario == user


@pytest.mark.django_db
def test_atualizacao_gasto_gera_log(user: User, categoria: Categoria) -> None:
    gasto = Gasto.objects.create(
        usuario=user,
        descricao="Almoço",
        valor=Decimal("25.00"),
        categoria=categoria,
        data=date.today(),
    )
    gasto.descricao = "Jantar"
    gasto.save()

    logs = LogAuditoria.objects.filter(modelo="Gasto", objeto_id=gasto.pk)
    assert logs.filter(acao="atualizado").exists()


@pytest.mark.django_db
def test_delecao_gasto_gera_log(user: User, categoria: Categoria) -> None:
    gasto = Gasto.objects.create(
        usuario=user,
        descricao="Almoço",
        valor=Decimal("25.00"),
        categoria=categoria,
        data=date.today(),
    )
    gasto_id = gasto.pk
    gasto.delete()

    log = LogAuditoria.objects.get(
        modelo="Gasto", objeto_id=gasto_id, acao="deletado"
    )
    assert log.acao == "deletado"


# ---------------------------------------------------------------------------
# Entrada
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_criacao_entrada_gera_log(user: User, fonte: Fonte) -> None:
    entrada = Entrada.objects.create(
        usuario=user,
        descricao="Pagamento",
        valor=Decimal("3000.00"),
        fonte=fonte,
        data=date.today(),
    )

    log = LogAuditoria.objects.get(modelo="Entrada", objeto_id=entrada.pk)
    assert log.acao == "criado"
    assert log.usuario == user


# ---------------------------------------------------------------------------
# Entrada — cenarios completos
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_atualizacao_entrada_gera_log(user: User, fonte: Fonte) -> None:
    entrada = Entrada.objects.create(
        usuario=user,
        descricao="Salario",
        valor=Decimal("3000.00"),
        fonte=fonte,
        data=date.today(),
    )
    entrada.descricao = "Bonus"
    entrada.save()

    log = LogAuditoria.objects.filter(
        modelo="Entrada", objeto_id=entrada.pk, acao="atualizado"
    ).first()
    assert log is not None


@pytest.mark.django_db
def test_delecao_entrada_gera_log(user: User, fonte: Fonte) -> None:
    entrada = Entrada.objects.create(
        usuario=user,
        descricao="Salario",
        valor=Decimal("3000.00"),
        fonte=fonte,
        data=date.today(),
    )
    entrada_id = entrada.pk
    entrada.delete()

    log = LogAuditoria.objects.get(
        modelo="Entrada", objeto_id=entrada_id, acao="deletado"
    )
    assert log.acao == "deletado"
