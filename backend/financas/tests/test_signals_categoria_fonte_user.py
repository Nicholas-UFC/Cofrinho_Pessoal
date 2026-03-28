from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth.models import User

from financas.models import Categoria, Fonte, Gasto, LogAuditoria

# ---------------------------------------------------------------------------
# Signals de auditoria — Categoria, Fonte, User e integridade do log
# ---------------------------------------------------------------------------
#
# Este arquivo testa os Django signals responsáveis por registrar no
# LogAuditoria toda criação, atualização e deleção de Categoria, Fonte e do
# próprio User.
#
# Por que testar esses sinais separadamente?
# — Categoria e Fonte são modelos de configuração (lookup tables) que o usuário
#   cria antes de registrar gastos ou entradas. Uma falha silenciosa no signal
#   dessas entidades deixaria lacunas na trilha de auditoria, dificultando
#   investigações de conformidade e rastreabilidade de dados.
# — O signal do User é especialmente crítico: criação e deleção de contas são
#   eventos de segurança que precisam ser auditados com username e detalhes
#   salvos — mesmo depois que o registro do usuário for removido do banco.
#
# O teste de choices de LogAuditoria garante uma regressão importante:
# `bulk_deletado` e `bulk_atualizado` precisam estar nas choices do model
# para que o campo `acao` passe na validação do Django sem erros silenciosos
# de banco.
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
# Categoria
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_criacao_categoria_gera_log(user: User) -> None:
    categoria = Categoria.objects.create(nome="Transporte", usuario=user)

    log = LogAuditoria.objects.get(modelo="Categoria", objeto_id=categoria.pk)
    assert log.acao == "criado"


@pytest.mark.django_db
def test_atualizacao_categoria_gera_log(user: User) -> None:
    categoria = Categoria.objects.create(nome="Lazer", usuario=user)
    categoria.nome = "Entretenimento"
    categoria.save()

    log = LogAuditoria.objects.filter(
        modelo="Categoria", objeto_id=categoria.pk, acao="atualizado"
    ).first()
    assert log is not None


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


@pytest.mark.django_db
def test_atualizacao_fonte_gera_log(user: User) -> None:
    fonte = Fonte.objects.create(nome="Freelance", usuario=user)
    fonte.nome = "Consultoria"
    fonte.save()

    log = LogAuditoria.objects.filter(
        modelo="Fonte", objeto_id=fonte.pk, acao="atualizado"
    ).first()
    assert log is not None


@pytest.mark.django_db
def test_delecao_fonte_gera_log(user: User) -> None:
    fonte = Fonte.objects.create(nome="Freelance", usuario=user)
    fonte_id = fonte.pk
    fonte.delete()

    log = LogAuditoria.objects.get(
        modelo="Fonte", objeto_id=fonte_id, acao="deletado"
    )
    assert log.acao == "deletado"


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_criacao_usuario_gera_log(db: None) -> None:
    # A criação de um novo usuário deve ser registrada imediatamente no log,
    # incluindo o username nos detalhes — essencial para rastrear quando e
    # qual conta foi criada, mesmo que o User seja deletado depois.
    novo_user = User.objects.create_user(username="novo", password="pass123")

    log = LogAuditoria.objects.get(
        modelo="User", objeto_id=novo_user.pk, acao="criado"
    )
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

    log = LogAuditoria.objects.get(
        modelo="User", objeto_id=user_id, acao="deletado"
    )
    assert log.detalhes["username"] == username


# ---------------------------------------------------------------------------
# Detalhes do log
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_log_armazena_detalhes(user: User, categoria: Categoria) -> None:
    # O campo `detalhes` do log deve armazenar os valores do objeto no momento
    # do evento, permitindo reconstruir o estado da entidade auditada.
    gasto = Gasto.objects.create(
        usuario=user,
        descricao="Mercado",
        valor=Decimal("80.00"),
        categoria=categoria,
        data=date.today(),
    )

    log = LogAuditoria.objects.get(
        modelo="Gasto", objeto_id=gasto.pk, acao="criado"
    )
    assert "descricao" in log.detalhes
    assert log.detalhes["descricao"] == "Mercado"


# ---------------------------------------------------------------------------
# Choices válidas (regressão — bulk_deletado e bulk_atualizado
# não estavam nas choices do model)
# ---------------------------------------------------------------------------


def test_choices_logauditoria_incluem_bulk() -> None:
    # Garante que as ações de bulk estão registradas nas choices do model.
    # Sem isso, o campo `acao` falha na validação do Django quando o signal
    # de bulk tenta salvar um log com essas ações.
    acoes = [choice[0] for choice in LogAuditoria.ACOES]
    assert "bulk_deletado" in acoes
    assert "bulk_atualizado" in acoes
