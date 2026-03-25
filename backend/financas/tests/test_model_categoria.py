from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import ProtectedError
from django.utils import timezone

from financas.models import Categoria, Gasto

# ---------------------------------------------------------------------------
# Fixture de usuário compartilhada
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
