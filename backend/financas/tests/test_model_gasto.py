from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone

from financas.models import Categoria, Gasto

_MSG_POSITIVO = "Apenas valores positivos são permitidos."


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def user(db: None) -> User:
    return User.objects.create_user(username="testuser", password="pass123")


# ---------------------------------------------------------------------------
# Gasto
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestGasto:
    @pytest.fixture
    def categoria(self, user: User) -> Categoria:
        return Categoria.objects.create(nome="Alimentação", usuario=user)

    def test_criacao(self, user: User, categoria: Categoria) -> None:
        gasto = Gasto.objects.create(
            descricao="Supermercado",
            valor=Decimal("150.00"),
            categoria=categoria,
            usuario=user,
            data=date.today(),
        )
        assert gasto.descricao == "Supermercado"
        assert gasto.valor == Decimal("150.00")
        assert gasto.categoria == categoria
        assert gasto.usuario == user
        assert gasto.data == date.today()
        assert gasto.criado_em is not None

    def test_str(self, user: User, categoria: Categoria) -> None:
        gasto = Gasto.objects.create(
            descricao="Farmácia",
            valor=Decimal("45.50"),
            categoria=categoria,
            usuario=user,
            data=date.today(),
        )
        assert str(gasto) == "Farmácia - R$ 45.50"

    def test_valor_aceita_decimal(
        self, user: User, categoria: Categoria
    ) -> None:
        gasto = Gasto.objects.create(
            descricao="Café",
            valor=Decimal("9.99"),
            categoria=categoria,
            usuario=user,
            data=date.today(),
        )
        assert gasto.valor == Decimal("9.99")

    def test_valor_negativo_lanca_validation_error(
        self, user: User, categoria: Categoria
    ) -> None:
        gasto = Gasto(
            descricao="Inválido",
            valor=Decimal("-10.00"),
            categoria=categoria,
            usuario=user,
            data=date.today(),
        )
        with pytest.raises(ValidationError) as exc_info:
            gasto.full_clean()
        assert _MSG_POSITIVO in str(exc_info.value)

    def test_valor_zero_lanca_validation_error(
        self, user: User, categoria: Categoria
    ) -> None:
        gasto = Gasto(
            descricao="Inválido",
            valor=Decimal("0.00"),
            categoria=categoria,
            usuario=user,
            data=date.today(),
        )
        with pytest.raises(ValidationError) as exc_info:
            gasto.full_clean()
        assert _MSG_POSITIVO in str(exc_info.value)

    def test_check_constraint_impede_valor_negativo_no_banco(
        self, user: User, categoria: Categoria
    ) -> None:
        with pytest.raises(IntegrityError):
            Gasto.objects.create(
                descricao="Inválido",
                valor=Decimal("-1.00"),
                categoria=categoria,
                usuario=user,
                data=date.today(),
            )

    def test_descricao_max_length(
        self, user: User, categoria: Categoria
    ) -> None:
        gasto = Gasto(
            descricao="A" * 201,
            valor=Decimal("10.00"),
            categoria=categoria,
            usuario=user,
            data=date.today(),
        )
        with pytest.raises(ValidationError):
            gasto.full_clean()

    def test_categoria_obrigatoria(self, user: User) -> None:
        gasto = Gasto(
            descricao="Sem categoria",
            valor=Decimal("10.00"),
            usuario=user,
            data=date.today(),
        )
        with pytest.raises((ValueError, IntegrityError, ValidationError)):
            gasto.full_clean()

    def test_criado_em_imutavel(
        self, user: User, categoria: Categoria
    ) -> None:
        gasto = Gasto.objects.create(
            descricao="Almoço",
            valor=Decimal("25.00"),
            categoria=categoria,
            usuario=user,
            data=date.today(),
        )
        criado_em_original = gasto.criado_em
        gasto.criado_em = timezone.now() + timedelta(days=10)
        gasto.save()
        gasto.refresh_from_db()
        assert gasto.criado_em == criado_em_original

    def test_ordering_mais_recente_primeiro(
        self, user: User, categoria: Categoria
    ) -> None:
        hoje = date.today()
        ontem = hoje - timedelta(days=1)
        gasto_ontem = Gasto.objects.create(
            descricao="Ontem",
            valor=Decimal("10.00"),
            categoria=categoria,
            usuario=user,
            data=ontem,
        )
        gasto_hoje = Gasto.objects.create(
            descricao="Hoje",
            valor=Decimal("20.00"),
            categoria=categoria,
            usuario=user,
            data=hoje,
        )
        gastos = list(Gasto.objects.all())
        assert gastos[0] == gasto_hoje
        assert gastos[1] == gasto_ontem
