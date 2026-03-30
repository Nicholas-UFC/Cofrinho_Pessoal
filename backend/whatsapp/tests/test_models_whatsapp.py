import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from whatsapp.models import SessaoConversa

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def user(db: None) -> User:
    return User.objects.create_user(username="testuser", password="pass123")


# ---------------------------------------------------------------------------
# SessaoConversa
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestSessaoConversa:
    def test_criacao(self) -> None:
        sessao = SessaoConversa.objects.create(chat_id="120363@g.us")
        assert sessao.pk is not None
        assert sessao.chat_id == "120363@g.us"

    def test_str(self) -> None:
        sessao = SessaoConversa.objects.create(chat_id="abc@g.us")
        assert str(sessao) == "Sessão abc@g.us [menu]"

    def test_estado_default_menu(self) -> None:
        sessao = SessaoConversa.objects.create(chat_id="a@g.us")
        assert sessao.estado == "menu"

    def test_dados_temporarios_default_dict_vazio(self) -> None:
        sessao = SessaoConversa.objects.create(chat_id="b@g.us")
        assert sessao.dados_temporarios == {}

    def test_chat_id_unico(self) -> None:
        SessaoConversa.objects.create(chat_id="unico@g.us")
        with pytest.raises(IntegrityError):
            SessaoConversa.objects.create(chat_id="unico@g.us")

    def test_usuario_pode_ser_nulo(self) -> None:
        sessao = SessaoConversa.objects.create(
            chat_id="c@g.us", usuario=None
        )
        assert sessao.usuario is None

    def test_usuario_pode_ser_vinculado(self, user: User) -> None:
        sessao = SessaoConversa.objects.create(
            chat_id="d@g.us", usuario=user
        )
        assert sessao.usuario == user

    def test_criado_em_preenchido_automaticamente(self) -> None:
        sessao = SessaoConversa.objects.create(chat_id="e@g.us")
        assert sessao.criado_em is not None

    def test_atualizado_em_preenchido_automaticamente(self) -> None:
        sessao = SessaoConversa.objects.create(chat_id="f@g.us")
        assert sessao.atualizado_em is not None

    def test_chat_id_max_length(self) -> None:
        sessao = SessaoConversa(chat_id="a" * 101)
        with pytest.raises(ValidationError):
            sessao.full_clean()

    def test_estados_choices_validos(self) -> None:
        codigos = [c for c, _ in SessaoConversa.ESTADOS]
        assert codigos == [
            "menu",
            "aguardando_valor_gasto",
            "aguardando_categoria_gasto",
            "confirmando_gasto",
            "aguardando_valor_entrada",
            "aguardando_fonte_entrada",
            "confirmando_entrada",
        ]

    def test_mudar_estado_e_salvar(self) -> None:
        sessao = SessaoConversa.objects.create(chat_id="g@g.us")
        sessao.estado = "aguardando_valor_gasto"
        sessao.save()
        sessao.refresh_from_db()
        assert sessao.estado == "aguardando_valor_gasto"

    def test_dados_temporarios_persiste_json(self) -> None:
        sessao = SessaoConversa.objects.create(chat_id="h@g.us")
        sessao.dados_temporarios = {"valor": "150,00", "categoria_id": 1}
        sessao.save()
        sessao.refresh_from_db()
        assert sessao.dados_temporarios["valor"] == "150,00"
        assert sessao.dados_temporarios["categoria_id"] == 1
