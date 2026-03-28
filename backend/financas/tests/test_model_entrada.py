from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone

from financas.models import Entrada, Fonte

# ---------------------------------------------------------------------------
# Testes de modelo — Entrada
# ---------------------------------------------------------------------------
#
# Esta suíte testa as regras de negócio do model Entrada diretamente via ORM,
# sem passar pela camada de API. A Entrada representa qualquer ingresso de
# dinheiro (salário, freelance, rendimento) e segue as mesmas regras de
# integridade do modelo Gasto:
#
# — Valor deve ser positivo: zero e negativo disparam ValidationError via
#   `full_clean()` e IntegrityError via CheckConstraint no banco.
# — `descricao` tem max_length=200; extrapolação dispara ValidationError.
# — `fonte` é obrigatória — Entrada sem Fonte viola a constraint de NOT NULL.
# — `criado_em` é auto_now_add e imutável: qualquer tentativa de sobrescrever
#   é silenciosamente ignorada pelo Django ao salvar.
# — Ordenação padrão: data mais recente primeiro.
# ---------------------------------------------------------------------------

_MSG_POSITIVO = "Apenas valores positivos são permitidos."


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def user(db: None) -> User:
    return User.objects.create_user(username="testuser", password="pass123")


# ---------------------------------------------------------------------------
# Entrada
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestEntrada:
    @pytest.fixture
    def fonte(self, user: User) -> Fonte:
        return Fonte.objects.create(nome="Salário", usuario=user)

    def test_criacao(self, user: User, fonte: Fonte) -> None:
        entrada = Entrada.objects.create(
            descricao="Salário Janeiro",
            valor=Decimal("3000.00"),
            fonte=fonte,
            usuario=user,
            data=date.today(),
        )
        assert entrada.descricao == "Salário Janeiro"
        assert entrada.valor == Decimal("3000.00")
        assert entrada.fonte == fonte
        assert entrada.usuario == user
        assert entrada.data == date.today()
        assert entrada.criado_em is not None

    def test_str(self, user: User, fonte: Fonte) -> None:
        entrada = Entrada.objects.create(
            descricao="Freelance",
            valor=Decimal("500.00"),
            fonte=fonte,
            usuario=user,
            data=date.today(),
        )
        assert str(entrada) == "Freelance - R$ 500.00"

    def test_valor_aceita_decimal(self, user: User, fonte: Fonte) -> None:
        entrada = Entrada.objects.create(
            descricao="Dividendos",
            valor=Decimal("123.45"),
            fonte=fonte,
            usuario=user,
            data=date.today(),
        )
        assert entrada.valor == Decimal("123.45")

    def test_valor_negativo_lanca_validation_error(
        self, user: User, fonte: Fonte
    ) -> None:
        entrada = Entrada(
            descricao="Inválido",
            valor=Decimal("-10.00"),
            fonte=fonte,
            usuario=user,
            data=date.today(),
        )
        with pytest.raises(ValidationError) as exc_info:
            entrada.full_clean()
        assert _MSG_POSITIVO in str(exc_info.value)

    def test_valor_zero_lanca_validation_error(
        self, user: User, fonte: Fonte
    ) -> None:
        entrada = Entrada(
            descricao="Inválido",
            valor=Decimal("0.00"),
            fonte=fonte,
            usuario=user,
            data=date.today(),
        )
        with pytest.raises(ValidationError) as exc_info:
            entrada.full_clean()
        assert _MSG_POSITIVO in str(exc_info.value)

    def test_check_constraint_impede_valor_negativo_no_banco(
        self, user: User, fonte: Fonte
    ) -> None:
        with pytest.raises(IntegrityError):
            Entrada.objects.create(
                descricao="Inválido",
                valor=Decimal("-1.00"),
                fonte=fonte,
                usuario=user,
                data=date.today(),
            )

    def test_descricao_max_length(self, user: User, fonte: Fonte) -> None:
        entrada = Entrada(
            descricao="A" * 201,
            valor=Decimal("10.00"),
            fonte=fonte,
            usuario=user,
            data=date.today(),
        )
        with pytest.raises(ValidationError):
            entrada.full_clean()

    def test_fonte_obrigatoria(self, user: User) -> None:
        entrada = Entrada(
            descricao="Sem fonte",
            valor=Decimal("10.00"),
            usuario=user,
            data=date.today(),
        )
        with pytest.raises((ValueError, IntegrityError, ValidationError)):
            entrada.full_clean()

    def test_criado_em_imutavel(self, user: User, fonte: Fonte) -> None:
        entrada = Entrada.objects.create(
            descricao="Salário",
            valor=Decimal("3000.00"),
            fonte=fonte,
            usuario=user,
            data=date.today(),
        )
        criado_em_original = entrada.criado_em
        entrada.criado_em = timezone.now() + timedelta(days=10)
        entrada.save()
        entrada.refresh_from_db()
        assert entrada.criado_em == criado_em_original

    def test_ordering_mais_recente_primeiro(
        self, user: User, fonte: Fonte
    ) -> None:
        hoje = date.today()
        ontem = hoje - timedelta(days=1)
        entrada_ontem = Entrada.objects.create(
            descricao="Ontem",
            valor=Decimal("1000.00"),
            fonte=fonte,
            usuario=user,
            data=ontem,
        )
        entrada_hoje = Entrada.objects.create(
            descricao="Hoje",
            valor=Decimal("2000.00"),
            fonte=fonte,
            usuario=user,
            data=hoje,
        )
        entradas = list(Entrada.objects.all())
        assert entradas[0] == entrada_hoje
        assert entradas[1] == entrada_ontem
