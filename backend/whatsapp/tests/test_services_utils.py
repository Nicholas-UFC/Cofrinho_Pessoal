from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth.models import User

from financas.models import Categoria, Entrada, Fonte, Gasto
from whatsapp.models import SessaoConversa
from whatsapp.services import (
    _escolher_item,
    _listar_categorias,
    _listar_fontes,
    _normalizar_corpo,
    _obter_resumo,
    _sem_cadastro,
)

# ---------------------------------------------------------------------------
# _normalizar_corpo — sem banco de dados
# ---------------------------------------------------------------------------


class TestNormalizarCorpo:
    def test_lowercases_maiusculas(self) -> None:
        assert _normalizar_corpo("MENU") == "menu"

    def test_remove_espacos(self) -> None:
        assert _normalizar_corpo("m e n u") == "menu"

    def test_combina_lower_e_sem_espacos(self) -> None:
        assert _normalizar_corpo("M E N U") == "menu"

    def test_string_vazia_permanece_vazia(self) -> None:
        assert _normalizar_corpo("") == ""

    def test_ja_normalizado_nao_altera(self) -> None:
        assert _normalizar_corpo("menu") == "menu"

    def test_numero_sem_espacos(self) -> None:
        assert _normalizar_corpo(" 1 ") == "1"


# ---------------------------------------------------------------------------
# _escolher_item — sem banco de dados
# ---------------------------------------------------------------------------


class TestEscolherItem:
    def test_escolhe_primeiro_item(self) -> None:
        itens = ["alfa", "beta", "gama"]
        assert _escolher_item(itens, "1") == "alfa"

    def test_escolhe_item_do_meio(self) -> None:
        itens = ["alfa", "beta", "gama"]
        assert _escolher_item(itens, "2") == "beta"

    def test_escolhe_ultimo_item(self) -> None:
        itens = ["alfa", "beta", "gama"]
        assert _escolher_item(itens, "3") == "gama"

    def test_indice_zero_retorna_none(self) -> None:
        assert _escolher_item(["alfa"], "0") is None

    def test_indice_fora_do_range_retorna_none(self) -> None:
        assert _escolher_item(["alfa", "beta"], "5") is None

    def test_texto_nao_numerico_retorna_none(self) -> None:
        assert _escolher_item(["alfa"], "x") is None

    def test_lista_vazia_retorna_none(self) -> None:
        assert _escolher_item([], "1") is None

    def test_numero_negativo_retorna_none(self) -> None:
        assert _escolher_item(["alfa"], "-1") is None


# ---------------------------------------------------------------------------
# Fixtures compartilhadas para testes com banco
# ---------------------------------------------------------------------------


@pytest.fixture
def user(db: None) -> User:
    return User.objects.create_user(username="testuser", password="pass123")


@pytest.fixture
def outro_user(db: None) -> User:
    return User.objects.create_user(username="outro", password="pass123")


@pytest.fixture
def sessao(db: None) -> SessaoConversa:
    s = SessaoConversa.objects.create(chat_id="test@g.us")
    s.estado = "aguardando_valor_gasto"
    s.dados_temporarios = {"valor": "100,00"}
    s.save()
    return s


# ---------------------------------------------------------------------------
# _listar_categorias — com banco
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestListarCategorias:
    def test_sem_categorias_retorna_string_vazia(
        self, user: User
    ) -> None:
        assert _listar_categorias(user) == ""

    def test_formato_numerado(self, user: User) -> None:
        Categoria.objects.create(nome="Alimentação", usuario=user)
        resultado = _listar_categorias(user)
        assert "1. Alimentação" in resultado

    def test_multiplas_categorias_numeradas(self, user: User) -> None:
        Categoria.objects.create(nome="Alimentação", usuario=user)
        Categoria.objects.create(nome="Transporte", usuario=user)
        resultado = _listar_categorias(user)
        assert "1." in resultado
        assert "2." in resultado

    def test_isolamento_por_usuario(
        self, user: User, outro_user: User
    ) -> None:
        Categoria.objects.create(nome="Só do Outro", usuario=outro_user)
        assert _listar_categorias(user) == ""

    def test_cada_categoria_em_linha_separada(self, user: User) -> None:
        Categoria.objects.create(nome="Alimentação", usuario=user)
        Categoria.objects.create(nome="Transporte", usuario=user)
        linhas = _listar_categorias(user).split("\n")
        assert len(linhas) == 2


# ---------------------------------------------------------------------------
# _listar_fontes — com banco
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestListarFontes:
    def test_sem_fontes_retorna_string_vazia(self, user: User) -> None:
        assert _listar_fontes(user) == ""

    def test_formato_numerado(self, user: User) -> None:
        Fonte.objects.create(nome="Salário", usuario=user)
        resultado = _listar_fontes(user)
        assert "1. Salário" in resultado

    def test_multiplas_fontes_numeradas(self, user: User) -> None:
        Fonte.objects.create(nome="Salário", usuario=user)
        Fonte.objects.create(nome="Freelance", usuario=user)
        resultado = _listar_fontes(user)
        assert "1." in resultado
        assert "2." in resultado

    def test_isolamento_por_usuario(
        self, user: User, outro_user: User
    ) -> None:
        Fonte.objects.create(nome="Só do Outro", usuario=outro_user)
        assert _listar_fontes(user) == ""

    def test_cada_fonte_em_linha_separada(self, user: User) -> None:
        Fonte.objects.create(nome="Salário", usuario=user)
        Fonte.objects.create(nome="Freelance", usuario=user)
        linhas = _listar_fontes(user).split("\n")
        assert len(linhas) == 2


# ---------------------------------------------------------------------------
# _sem_cadastro — com banco
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestSemCadastro:
    def test_reseta_estado_para_menu(
        self, sessao: SessaoConversa
    ) -> None:
        _sem_cadastro(sessao, "categoria")
        sessao.refresh_from_db()
        assert sessao.estado == "menu"

    def test_limpa_dados_temporarios(
        self, sessao: SessaoConversa
    ) -> None:
        _sem_cadastro(sessao, "categoria")
        sessao.refresh_from_db()
        assert sessao.dados_temporarios == {}

    def test_mensagem_contem_tipo_categoria(
        self, sessao: SessaoConversa
    ) -> None:
        msg = _sem_cadastro(sessao, "categoria")
        assert "categoria" in msg

    def test_mensagem_contem_tipo_fonte(
        self, sessao: SessaoConversa
    ) -> None:
        msg = _sem_cadastro(sessao, "fonte")
        assert "fonte" in msg

    def test_mensagem_orienta_usar_app(
        self, sessao: SessaoConversa
    ) -> None:
        msg = _sem_cadastro(sessao, "categoria")
        assert "app" in msg.lower()


# ---------------------------------------------------------------------------
# _obter_resumo — com banco
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestObterResumo:
    def test_sem_registros_retorna_zeros(self, user: User) -> None:
        resultado = _obter_resumo(user)
        assert "0.00" in resultado

    def test_formato_inclui_mes_e_ano(self, user: User) -> None:
        resultado = _obter_resumo(user)
        mes_ano = date.today().strftime("%m/%Y")
        assert mes_ano in resultado

    def test_calcula_total_gastos(self, user: User) -> None:
        categoria = Categoria.objects.create(
            nome="Alimentação", usuario=user
        )
        Gasto.objects.create(
            descricao="Mercado",
            valor=Decimal("100.00"),
            categoria=categoria,
            usuario=user,
            data=date.today(),
        )
        resultado = _obter_resumo(user)
        assert "100.00" in resultado

    def test_calcula_total_entradas(self, user: User) -> None:
        fonte = Fonte.objects.create(nome="Salário", usuario=user)
        Entrada.objects.create(
            descricao="Salário",
            valor=Decimal("500.00"),
            fonte=fonte,
            usuario=user,
            data=date.today(),
        )
        resultado = _obter_resumo(user)
        assert "500.00" in resultado

    def test_calcula_saldo_correto(self, user: User) -> None:
        categoria = Categoria.objects.create(
            nome="Alimentação", usuario=user
        )
        fonte = Fonte.objects.create(nome="Salário", usuario=user)
        Gasto.objects.create(
            descricao="Mercado",
            valor=Decimal("100.00"),
            categoria=categoria,
            usuario=user,
            data=date.today(),
        )
        Entrada.objects.create(
            descricao="Salário",
            valor=Decimal("500.00"),
            fonte=fonte,
            usuario=user,
            data=date.today(),
        )
        resultado = _obter_resumo(user)
        assert "400.00" in resultado  # saldo = 500 - 100
