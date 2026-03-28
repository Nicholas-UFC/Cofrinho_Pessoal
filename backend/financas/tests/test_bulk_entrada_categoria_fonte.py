from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth.models import User

from financas.models import Categoria, Entrada, Fonte, LogAuditoria

# ---------------------------------------------------------------------------
# Operações bulk — Entrada, Categoria e Fonte
# ---------------------------------------------------------------------------
#
# O Django não dispara signals `post_save` e `post_delete` em operações de
# queryset como `.update()` e `.delete()` — ele chama o banco diretamente,
# sem instanciar os objetos. Para garantir auditoria completa, o projeto usa
# custom QuerySets que interceptam essas operações e geram LogAuditoria
# manualmente antes de executar o SQL.
#
# Este arquivo testa as operações bulk nos modelos Entrada, Categoria e Fonte.
# Para Gasto (o modelo principal), os testes estão em `test_bulk.py`.
#
# O que é verificado em cada modelo:
# — bulk_delete: um LogAuditoria com acao="bulk_deletado" deve ser criado para
#   cada objeto removido, com o `objeto_id` correto no log.
# — bulk_update: um LogAuditoria com acao="bulk_atualizado" deve ser criado,
#   registrando quais campos foram alterados e com quais valores novos.
# ---------------------------------------------------------------------------


@pytest.fixture
def user(db: None) -> User:
    return User.objects.create_user(username="testuser", password="pass123")


@pytest.fixture
def fonte(user: User) -> Fonte:
    return Fonte.objects.create(nome="Salário", usuario=user)


# ---------------------------------------------------------------------------
# Entrada bulk
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_bulk_delete_entrada_gera_log(user: User, fonte: Fonte) -> None:
    entrada = Entrada.objects.create(
        usuario=user,
        descricao="Salario",
        valor=Decimal("3000.00"),
        fonte=fonte,
        data=date.today(),
    )
    entrada_id = entrada.pk

    Entrada.objects.filter(pk=entrada_id).delete()

    log = LogAuditoria.objects.get(modelo="Entrada", acao="bulk_deletado")
    assert log.objeto_id == entrada_id


@pytest.mark.django_db
def test_bulk_update_entrada_gera_log(user: User, fonte: Fonte) -> None:
    entrada = Entrada.objects.create(
        usuario=user,
        descricao="Salario",
        valor=Decimal("3000.00"),
        fonte=fonte,
        data=date.today(),
    )

    Entrada.objects.filter(pk=entrada.pk).update(descricao="Bonus")

    log = LogAuditoria.objects.get(modelo="Entrada", acao="bulk_atualizado")
    assert log.detalhes["campos"]["descricao"] == "Bonus"


# ---------------------------------------------------------------------------
# Categoria bulk
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_bulk_delete_categoria_gera_log(user: User) -> None:
    categoria = Categoria.objects.create(nome="Lazer", usuario=user)
    categoria_id = categoria.pk

    Categoria.objects.filter(pk=categoria_id).delete()

    log = LogAuditoria.objects.get(modelo="Categoria", acao="bulk_deletado")
    assert log.objeto_id == categoria_id


@pytest.mark.django_db
def test_bulk_update_categoria_gera_log(user: User) -> None:
    categoria = Categoria.objects.create(nome="Lazer", usuario=user)

    Categoria.objects.filter(pk=categoria.pk).update(nome="Entretenimento")

    log = LogAuditoria.objects.get(modelo="Categoria", acao="bulk_atualizado")
    assert log.detalhes["campos"]["nome"] == "Entretenimento"


# ---------------------------------------------------------------------------
# Fonte bulk
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_bulk_delete_fonte_gera_log(user: User) -> None:
    fonte = Fonte.objects.create(nome="Freelance", usuario=user)
    fonte_id = fonte.pk

    Fonte.objects.filter(pk=fonte_id).delete()

    log = LogAuditoria.objects.get(modelo="Fonte", acao="bulk_deletado")
    assert log.objeto_id == fonte_id


@pytest.mark.django_db
def test_bulk_update_fonte_gera_log(user: User) -> None:
    fonte = Fonte.objects.create(nome="Freelance", usuario=user)

    Fonte.objects.filter(pk=fonte.pk).update(nome="Consultoria")

    log = LogAuditoria.objects.get(modelo="Fonte", acao="bulk_atualizado")
    assert log.detalhes["campos"]["nome"] == "Consultoria"
