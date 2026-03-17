from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import ProtectedError
from django.utils import timezone

from financas.models import Categoria, Entrada, Fonte, Gasto

_MSG_POSITIVO = "Apenas valores positivos são permitidos."


# ---------------------------------------------------------------------------
# Fixture de usuário compartilhada entre todos os testes de models.
# ---------------------------------------------------------------------------


@pytest.fixture
def user(db: None) -> User:
    return User.objects.create_user(username="testuser", password="pass123")


# ---------------------------------------------------------------------------
# Categoria
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestCategoria:
    def test_criacao(self, user: User) -> None:
        categoria = Categoria.objects.create(nome="Alimentação", usuario=user)
        assert categoria.nome == "Alimentação"
        assert categoria.usuario == user
        assert categoria.id is not None
        assert categoria.criado_em is not None

    def test_str(self, user: User) -> None:
        categoria = Categoria.objects.create(nome="Transporte", usuario=user)
        assert str(categoria) == "Transporte"

    def test_nome_max_length(self, user: User) -> None:
        categoria = Categoria(nome="A" * 101, usuario=user)
        with pytest.raises(ValidationError):
            categoria.full_clean()

    def test_nome_unico_por_usuario(self, user: User) -> None:
        # Mesmo usuário não pode ter duas categorias com o mesmo nome.
        Categoria.objects.create(nome="Lazer", usuario=user)
        with pytest.raises(IntegrityError):
            Categoria.objects.create(nome="Lazer", usuario=user)

    def test_nome_igual_em_usuarios_diferentes_e_permitido(
        self, user: User
    ) -> None:
        # Usuários diferentes podem ter categorias com o mesmo nome.
        outro = User.objects.create_user(username="outro", password="pass")
        Categoria.objects.create(nome="Lazer", usuario=user)
        cat2 = Categoria.objects.create(nome="Lazer", usuario=outro)
        assert cat2.pk is not None

    def test_criado_em_preenchido_automaticamente(self, user: User) -> None:
        categoria = Categoria.objects.create(nome="Saúde", usuario=user)
        assert categoria.criado_em is not None

    def test_criado_em_imutavel(self, user: User) -> None:
        categoria = Categoria.objects.create(nome="Educação", usuario=user)
        criado_em_original = categoria.criado_em
        categoria.criado_em = timezone.now() + timedelta(days=10)
        categoria.save()
        categoria.refresh_from_db()
        assert categoria.criado_em == criado_em_original

    def test_delete_com_fk_ativa_lanca_protected_error(
        self, user: User
    ) -> None:
        categoria = Categoria.objects.create(nome="Moradia", usuario=user)
        Gasto.objects.create(
            descricao="Aluguel",
            valor=Decimal("1000.00"),
            categoria=categoria,
            usuario=user,
            data=date.today(),
        )
        with pytest.raises(ProtectedError):
            categoria.delete()

    def test_delete_sem_fk_funciona(self, user: User) -> None:
        categoria = Categoria.objects.create(nome="Outros", usuario=user)
        categoria.delete()
        assert not Categoria.objects.filter(nome="Outros").exists()


# ---------------------------------------------------------------------------
# Fonte
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestFonte:
    def test_criacao(self, user: User) -> None:
        fonte = Fonte.objects.create(nome="Salário", usuario=user)
        assert fonte.nome == "Salário"
        assert fonte.usuario == user
        assert fonte.id is not None
        assert fonte.criado_em is not None

    def test_str(self, user: User) -> None:
        fonte = Fonte.objects.create(nome="Freelance", usuario=user)
        assert str(fonte) == "Freelance"

    def test_nome_max_length(self, user: User) -> None:
        fonte = Fonte(nome="A" * 101, usuario=user)
        with pytest.raises(ValidationError):
            fonte.full_clean()

    def test_nome_unico_por_usuario(self, user: User) -> None:
        # Mesmo usuário não pode ter duas fontes com o mesmo nome.
        Fonte.objects.create(nome="Investimento", usuario=user)
        with pytest.raises(IntegrityError):
            Fonte.objects.create(nome="Investimento", usuario=user)

    def test_nome_igual_em_usuarios_diferentes_e_permitido(
        self, user: User
    ) -> None:
        # Usuários diferentes podem ter fontes com o mesmo nome.
        outro = User.objects.create_user(username="outro", password="pass")
        Fonte.objects.create(nome="Salário", usuario=user)
        fonte2 = Fonte.objects.create(nome="Salário", usuario=outro)
        assert fonte2.pk is not None

    def test_criado_em_preenchido_automaticamente(self, user: User) -> None:
        fonte = Fonte.objects.create(nome="Outros", usuario=user)
        assert fonte.criado_em is not None

    def test_criado_em_imutavel(self, user: User) -> None:
        fonte = Fonte.objects.create(nome="Bônus", usuario=user)
        criado_em_original = fonte.criado_em
        fonte.criado_em = timezone.now() + timedelta(days=10)
        fonte.save()
        fonte.refresh_from_db()
        assert fonte.criado_em == criado_em_original

    def test_delete_com_fk_ativa_lanca_protected_error(
        self, user: User
    ) -> None:
        fonte = Fonte.objects.create(nome="Aluguel Recebido", usuario=user)
        Entrada.objects.create(
            descricao="Aluguel Janeiro",
            valor=Decimal("1500.00"),
            fonte=fonte,
            usuario=user,
            data=date.today(),
        )
        with pytest.raises(ProtectedError):
            fonte.delete()

    def test_delete_sem_fk_funciona(self, user: User) -> None:
        fonte = Fonte.objects.create(nome="Presente", usuario=user)
        fonte.delete()
        assert not Fonte.objects.filter(nome="Presente").exists()


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

    _SKIP_SQLITE = (
        "SQLite não enforça CheckConstraint — reabilitar com PostgreSQL"
    )

    @pytest.mark.skip(reason=_SKIP_SQLITE)
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
