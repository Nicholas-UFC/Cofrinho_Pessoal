from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth.models import User

from financas.models import Categoria, Entrada, Fonte, Gasto, LogAuditoria


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

    log = LogAuditoria.objects.get(modelo="Gasto", objeto_id=gasto_id, acao="deletado")
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
# Categoria
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_criacao_categoria_gera_log(user: User) -> None:
    categoria = Categoria.objects.create(nome="Transporte", usuario=user)

    log = LogAuditoria.objects.get(modelo="Categoria", objeto_id=categoria.pk)
    assert log.acao == "criado"


@pytest.mark.django_db
def test_delecao_categoria_gera_log(user: User) -> None:
    categoria = Categoria.objects.create(nome="Lazer", usuario=user)
    categoria_id = categoria.pk
    categoria.delete()

    log = LogAuditoria.objects.get(
        modelo="Categoria", objeto_id=categoria_id, acao="deletado"
    )
    assert log.acao == "deletado"


# ---------------------------------------------------------------------------
# Fonte
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_criacao_fonte_gera_log(user: User) -> None:
    fonte = Fonte.objects.create(nome="Freelance", usuario=user)

    log = LogAuditoria.objects.get(modelo="Fonte", objeto_id=fonte.pk)
    assert log.acao == "criado"


# ---------------------------------------------------------------------------
# Detalhes do log
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_log_armazena_detalhes(user: User, categoria: Categoria) -> None:
    gasto = Gasto.objects.create(
        usuario=user,
        descricao="Mercado",
        valor=Decimal("80.00"),
        categoria=categoria,
        data=date.today(),
    )

    log = LogAuditoria.objects.get(modelo="Gasto", objeto_id=gasto.pk, acao="criado")
    assert "descricao" in log.detalhes
    assert log.detalhes["descricao"] == "Mercado"


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_criacao_usuario_gera_log(db: None) -> None:
    novo_user = User.objects.create_user(username="novo", password="pass123")

    log = LogAuditoria.objects.get(modelo="User", objeto_id=novo_user.pk, acao="criado")
    assert log.detalhes["username"] == "novo"


@pytest.mark.django_db
def test_atualizacao_usuario_gera_log(user: User) -> None:
    user.email = "novo@email.com"
    user.save()

    log = LogAuditoria.objects.filter(
        modelo="User", objeto_id=user.pk, acao="atualizado"
    ).first()
    assert log is not None
    assert log.detalhes["email"] == "novo@email.com"


@pytest.mark.django_db
def test_delecao_usuario_gera_log(user: User) -> None:
    user_id = user.pk
    username = user.username
    user.delete()

    log = LogAuditoria.objects.get(modelo="User", objeto_id=user_id, acao="deletado")
    assert log.detalhes["username"] == username
