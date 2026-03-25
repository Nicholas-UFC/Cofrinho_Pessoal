from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth.models import User

from financas.models import Categoria, Entrada, Fonte, Gasto, LogAuditoria


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
