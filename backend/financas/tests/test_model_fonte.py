from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import ProtectedError
from django.utils import timezone

from financas.models import Entrada, Fonte

# ---------------------------------------------------------------------------
# Testes de modelo — Fonte
# ---------------------------------------------------------------------------
#
# Fonte é o modelo de lookup para classificar entradas financeiras (ex:
# "Salário", "Freelance", "Dividendos"). Segue as mesmas regras de Categoria:
#
# — Nome tem max_length=100; ultrapassar dispara ValidationError.
# — O par (nome, usuario) é único por usuário; duplicata gera IntegrityError.
#   Usuários diferentes podem ter fontes com o mesmo nome.
# — `criado_em` é auto_now_add e imutável.
# — Deletar uma Fonte que ainda tem Entradas associadas lança ProtectedError.
# — Deletar uma Fonte sem Entradas funciona normalmente.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Fixture de usuário compartilhada
# ---------------------------------------------------------------------------


@pytest.fixture
def user(db: None) -> User:
    return User.objects.create_user(username="testuser", password="pass123")


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
