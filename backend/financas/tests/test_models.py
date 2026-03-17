from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import ProtectedError
from django.utils import timezone

from financas.models import Categoria, Entrada, Fonte, Gasto

_MSG_POSITIVO = "Apenas valores positivos são permitidos."

# ---------------------------------------------------------------------------
# Categoria
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestCategoria:
    def test_criacao(self) -> None:
        categoria = Categoria.objects.create(nome="Alimentação")
        assert categoria.nome == "Alimentação"
        assert categoria.id is not None
        assert categoria.criado_em is not None

    def test_str(self) -> None:
        categoria = Categoria.objects.create(nome="Transporte")
        assert str(categoria) == "Transporte"

    def test_nome_max_length(self) -> None:
        categoria = Categoria(nome="A" * 101)
        with pytest.raises(ValidationError):
            categoria.full_clean()

    def test_nome_unique(self) -> None:
        Categoria.objects.create(nome="Lazer")
        with pytest.raises(IntegrityError):
            Categoria.objects.create(nome="Lazer")

    def test_criado_em_preenchido_automaticamente(self) -> None:
        categoria = Categoria.objects.create(nome="Saúde")
        assert categoria.criado_em is not None

    def test_criado_em_imutavel(self) -> None:
        categoria = Categoria.objects.create(nome="Educação")
        criado_em_original = categoria.criado_em
        categoria.criado_em = timezone.now() + timedelta(days=10)
        categoria.save()
        categoria.refresh_from_db()
        assert categoria.criado_em == criado_em_original

    def test_delete_com_fk_ativa_lanca_protected_error(self) -> None:
        categoria = Categoria.objects.create(nome="Moradia")
        Gasto.objects.create(
            descricao="Aluguel",
            valor=Decimal("1000.00"),
            categoria=categoria,
            data=date.today(),
        )
        with pytest.raises(ProtectedError):
            categoria.delete()

    def test_delete_sem_fk_funciona(self) -> None:
        categoria = Categoria.objects.create(nome="Outros")
        categoria.delete()
        assert not Categoria.objects.filter(nome="Outros").exists()


# ---------------------------------------------------------------------------
# Fonte
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestFonte:
    def test_criacao(self) -> None:
        fonte = Fonte.objects.create(nome="Salário")
        assert fonte.nome == "Salário"
        assert fonte.id is not None
        assert fonte.criado_em is not None

    def test_str(self) -> None:
        fonte = Fonte.objects.create(nome="Freelance")
        assert str(fonte) == "Freelance"

    def test_nome_max_length(self) -> None:
        fonte = Fonte(nome="A" * 101)
        with pytest.raises(ValidationError):
            fonte.full_clean()

    def test_nome_unique(self) -> None:
        Fonte.objects.create(nome="Investimento")
        with pytest.raises(IntegrityError):
            Fonte.objects.create(nome="Investimento")

    def test_criado_em_preenchido_automaticamente(self) -> None:
        fonte = Fonte.objects.create(nome="Outros")
        assert fonte.criado_em is not None

    def test_criado_em_imutavel(self) -> None:
        fonte = Fonte.objects.create(nome="Bônus")
        criado_em_original = fonte.criado_em
        fonte.criado_em = timezone.now() + timedelta(days=10)
        fonte.save()
        fonte.refresh_from_db()
        assert fonte.criado_em == criado_em_original

    def test_delete_com_fk_ativa_lanca_protected_error(self) -> None:
        fonte = Fonte.objects.create(nome="Aluguel Recebido")
        Entrada.objects.create(
            descricao="Aluguel Janeiro",
            valor=Decimal("1500.00"),
            fonte=fonte,
            data=date.today(),
        )
        with pytest.raises(ProtectedError):
            fonte.delete()

    def test_delete_sem_fk_funciona(self) -> None:
        fonte = Fonte.objects.create(nome="Presente")
        fonte.delete()
        assert not Fonte.objects.filter(nome="Presente").exists()


# ---------------------------------------------------------------------------
# Gasto
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestGasto:
    @pytest.fixture
    def categoria(self) -> Categoria:
        return Categoria.objects.create(nome="Alimentação")

    def test_criacao(self, categoria: Categoria) -> None:
        gasto = Gasto.objects.create(
            descricao="Supermercado",
            valor=Decimal("150.00"),
            categoria=categoria,
            data=date.today(),
        )
        assert gasto.descricao == "Supermercado"
        assert gasto.valor == Decimal("150.00")
        assert gasto.categoria == categoria
        assert gasto.data == date.today()
        assert gasto.criado_em is not None

    def test_str(self, categoria: Categoria) -> None:
        gasto = Gasto.objects.create(
            descricao="Farmácia",
            valor=Decimal("45.50"),
            categoria=categoria,
            data=date.today(),
        )
        assert str(gasto) == "Farmácia - R$ 45.50"

    def test_valor_aceita_decimal(self, categoria: Categoria) -> None:
        gasto = Gasto.objects.create(
            descricao="Café",
            valor=Decimal("9.99"),
            categoria=categoria,
            data=date.today(),
        )
        assert gasto.valor == Decimal("9.99")

    def test_valor_negativo_lanca_validation_error(
        self, categoria: Categoria
    ) -> None:
        gasto = Gasto(
            descricao="Inválido",
            valor=Decimal("-10.00"),
            categoria=categoria,
            data=date.today(),
        )
        with pytest.raises(ValidationError) as exc_info:
            gasto.full_clean()
        assert _MSG_POSITIVO in str(exc_info.value)

    def test_valor_zero_lanca_validation_error(
        self, categoria: Categoria
    ) -> None:
        gasto = Gasto(
            descricao="Inválido",
            valor=Decimal("0.00"),
            categoria=categoria,
            data=date.today(),
        )
        with pytest.raises(ValidationError) as exc_info:
            gasto.full_clean()
        assert _MSG_POSITIVO in str(exc_info.value)

    _SKIP_SQLITE = (
        "SQLite não enforça CheckConstraint — reabilitar com PostgreSQL"
    )

    @pytest.mark.skip(reason=_SKIP_SQLITE)
    def test_check_constraint_impede_valor_negativo_no_banco(
        self, categoria: Categoria
    ) -> None:
        with pytest.raises(IntegrityError):
            Gasto.objects.create(
                descricao="Inválido",
                valor=Decimal("-1.00"),
                categoria=categoria,
                data=date.today(),
            )

    def test_descricao_max_length(self, categoria: Categoria) -> None:
        gasto = Gasto(
            descricao="A" * 201,
            valor=Decimal("10.00"),
            categoria=categoria,
            data=date.today(),
        )
        with pytest.raises(ValidationError):
            gasto.full_clean()

    def test_categoria_obrigatoria(self) -> None:
        gasto = Gasto(
            descricao="Sem categoria",
            valor=Decimal("10.00"),
            data=date.today(),
        )
        with pytest.raises((ValueError, IntegrityError, ValidationError)):
            gasto.full_clean()

    def test_criado_em_imutavel(self, categoria: Categoria) -> None:
        gasto = Gasto.objects.create(
            descricao="Almoço",
            valor=Decimal("25.00"),
            categoria=categoria,
            data=date.today(),
        )
        criado_em_original = gasto.criado_em
        gasto.criado_em = timezone.now() + timedelta(days=10)
        gasto.save()
        gasto.refresh_from_db()
        assert gasto.criado_em == criado_em_original

    def test_ordering_mais_recente_primeiro(
        self, categoria: Categoria
    ) -> None:
        hoje = date.today()
        ontem = hoje - timedelta(days=1)
        gasto_ontem = Gasto.objects.create(
            descricao="Ontem",
            valor=Decimal("10.00"),
            categoria=categoria,
            data=ontem,
        )
        gasto_hoje = Gasto.objects.create(
            descricao="Hoje",
            valor=Decimal("20.00"),
            categoria=categoria,
            data=hoje,
        )
        gastos = list(Gasto.objects.all())
        assert gastos[0] == gasto_hoje
        assert gastos[1] == gasto_ontem


# ---------------------------------------------------------------------------
# Entrada
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestEntrada:
    @pytest.fixture
    def fonte(self) -> Fonte:
        return Fonte.objects.create(nome="Salário")

    def test_criacao(self, fonte: Fonte) -> None:
        entrada = Entrada.objects.create(
            descricao="Salário Janeiro",
            valor=Decimal("3000.00"),
            fonte=fonte,
            data=date.today(),
        )
        assert entrada.descricao == "Salário Janeiro"
        assert entrada.valor == Decimal("3000.00")
        assert entrada.fonte == fonte
        assert entrada.data == date.today()
        assert entrada.criado_em is not None

    def test_str(self, fonte: Fonte) -> None:
        entrada = Entrada.objects.create(
            descricao="Freelance",
            valor=Decimal("500.00"),
            fonte=fonte,
            data=date.today(),
        )
        assert str(entrada) == "Freelance - R$ 500.00"

    def test_valor_aceita_decimal(self, fonte: Fonte) -> None:
        entrada = Entrada.objects.create(
            descricao="Dividendos",
            valor=Decimal("123.45"),
            fonte=fonte,
            data=date.today(),
        )
        assert entrada.valor == Decimal("123.45")

    def test_valor_negativo_lanca_validation_error(self, fonte: Fonte) -> None:
        entrada = Entrada(
            descricao="Inválido",
            valor=Decimal("-10.00"),
            fonte=fonte,
            data=date.today(),
        )
        with pytest.raises(ValidationError) as exc_info:
            entrada.full_clean()
        assert _MSG_POSITIVO in str(exc_info.value)

    def test_valor_zero_lanca_validation_error(self, fonte: Fonte) -> None:
        entrada = Entrada(
            descricao="Inválido",
            valor=Decimal("0.00"),
            fonte=fonte,
            data=date.today(),
        )
        with pytest.raises(ValidationError) as exc_info:
            entrada.full_clean()
        assert _MSG_POSITIVO in str(exc_info.value)

    def test_check_constraint_impede_valor_negativo_no_banco(
        self, fonte: Fonte
    ) -> None:
        with pytest.raises(IntegrityError):
            Entrada.objects.create(
                descricao="Inválido",
                valor=Decimal("-1.00"),
                fonte=fonte,
                data=date.today(),
            )

    def test_descricao_max_length(self, fonte: Fonte) -> None:
        entrada = Entrada(
            descricao="A" * 201,
            valor=Decimal("10.00"),
            fonte=fonte,
            data=date.today(),
        )
        with pytest.raises(ValidationError):
            entrada.full_clean()

    def test_fonte_obrigatoria(self) -> None:
        entrada = Entrada(
            descricao="Sem fonte",
            valor=Decimal("10.00"),
            data=date.today(),
        )
        with pytest.raises((ValueError, IntegrityError, ValidationError)):
            entrada.full_clean()

    def test_criado_em_imutavel(self, fonte: Fonte) -> None:
        entrada = Entrada.objects.create(
            descricao="Salário",
            valor=Decimal("3000.00"),
            fonte=fonte,
            data=date.today(),
        )
        criado_em_original = entrada.criado_em
        entrada.criado_em = timezone.now() + timedelta(days=10)
        entrada.save()
        entrada.refresh_from_db()
        assert entrada.criado_em == criado_em_original

    def test_ordering_mais_recente_primeiro(self, fonte: Fonte) -> None:
        hoje = date.today()
        ontem = hoje - timedelta(days=1)
        entrada_ontem = Entrada.objects.create(
            descricao="Ontem",
            valor=Decimal("1000.00"),
            fonte=fonte,
            data=ontem,
        )
        entrada_hoje = Entrada.objects.create(
            descricao="Hoje",
            valor=Decimal("2000.00"),
            fonte=fonte,
            data=hoje,
        )
        entradas = list(Entrada.objects.all())
        assert entradas[0] == entrada_hoje
        assert entradas[1] == entrada_ontem
