from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth.models import User

from financas.models import Categoria, Gasto, LogAuditoria

# ---------------------------------------------------------------------------
# Operações bulk — Gasto
# ---------------------------------------------------------------------------
#
# O Django não dispara signals `post_save` e `post_delete` para operações de
# queryset como `.update()` e `.delete()` — ele acessa o banco diretamente
# sem instanciar os objetos individualmente. Para garantir que a trilha de
# auditoria permaneça completa mesmo nessas situações, o projeto usa custom
# QuerySets que interceptam as operações bulk e geram LogAuditoria antes de
# executar o SQL.
#
# Este arquivo testa as operações bulk no modelo Gasto (o mais crítico, por
# ser o modelo de maior volume de escritas no sistema). Para Entrada, Categoria
# e Fonte, os testes estão em `test_bulk_entrada_categoria_fonte.py`.
#
# O que é verificado:
# — bulk_delete em múltiplos registros: deve gerar um LogAuditoria por objeto
#   removido, com os IDs afetados salvos nos detalhes do log.
# — bulk_update: deve gerar um log com os campos e valores novos registrados
#   em `detalhes["campos"]`, permitindo reconstruir o que mudou.
# ---------------------------------------------------------------------------


@pytest.fixture
def user(db: None) -> User:
    return User.objects.create_user(username="testuser", password="pass123")


@pytest.fixture
def categoria(user: User) -> Categoria:
    return Categoria.objects.create(nome="Alimentação", usuario=user)


# ---------------------------------------------------------------------------
# Bulk delete
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_bulk_delete_gasto_gera_log(user: User, categoria: Categoria) -> None:
    gasto1 = Gasto.objects.create(
        usuario=user,
        descricao="Almoço",
        valor=Decimal("30.00"),
        categoria=categoria,
        data=date.today(),
    )
    gasto2 = Gasto.objects.create(
        usuario=user,
        descricao="Jantar",
        valor=Decimal("40.00"),
        categoria=categoria,
        data=date.today(),
    )
    ids = [gasto1.pk, gasto2.pk]

    Gasto.objects.filter(pk__in=ids).delete()

    logs = LogAuditoria.objects.filter(modelo="Gasto", acao="bulk_deletado")
    assert logs.count() == 2
    assert logs.filter(objeto_id=gasto1.pk).exists()
    assert logs.filter(objeto_id=gasto2.pk).exists()


@pytest.mark.django_db
def test_bulk_delete_registra_ids_afetados(
    user: User, categoria: Categoria
) -> None:
    gasto = Gasto.objects.create(
        usuario=user,
        descricao="Almoço",
        valor=Decimal("30.00"),
        categoria=categoria,
        data=date.today(),
    )
    gasto_id = gasto.pk

    Gasto.objects.filter(pk=gasto_id).delete()

    log = LogAuditoria.objects.get(modelo="Gasto", acao="bulk_deletado")
    assert gasto_id in log.detalhes["ids_afetados"]


# ---------------------------------------------------------------------------
# Bulk update
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_bulk_update_gasto_gera_log(user: User, categoria: Categoria) -> None:
    gasto = Gasto.objects.create(
        usuario=user,
        descricao="Almoço",
        valor=Decimal("30.00"),
        categoria=categoria,
        data=date.today(),
    )

    Gasto.objects.filter(pk=gasto.pk).update(descricao="Almoço atualizado")

    log = LogAuditoria.objects.filter(
        modelo="Gasto", acao="bulk_atualizado"
    ).first()
    assert log is not None
    assert log.objeto_id == gasto.pk


@pytest.mark.django_db
def test_bulk_update_registra_campos_alterados(
    user: User, categoria: Categoria
) -> None:
    gasto = Gasto.objects.create(
        usuario=user,
        descricao="Almoço",
        valor=Decimal("30.00"),
        categoria=categoria,
        data=date.today(),
    )

    Gasto.objects.filter(pk=gasto.pk).update(descricao="Novo nome")

    log = LogAuditoria.objects.get(modelo="Gasto", acao="bulk_atualizado")
    assert "descricao" in log.detalhes["campos"]
    assert log.detalhes["campos"]["descricao"] == "Novo nome"
