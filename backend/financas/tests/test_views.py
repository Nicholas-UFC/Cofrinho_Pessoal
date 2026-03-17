from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from financas.models import Categoria, Entrada, Fonte, Gasto

# ---------------------------------------------------------------------------
# Fixtures compartilhadas
# ---------------------------------------------------------------------------


@pytest.fixture
def client() -> APIClient:
    # Cliente da API sem autenticação — usado para testar rotas protegidas.
    return APIClient()


@pytest.fixture
def user(db: None) -> User:
    return User.objects.create_user(
        username="testuser", password="testpass123"
    )


@pytest.fixture
def auth_client(client: APIClient, user: User) -> APIClient:
    # Cliente autenticado via JWT para os testes normais.
    response = client.post(
        "/api/token/",
        {"username": "testuser", "password": "testpass123"},
    )
    token = response.data["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.fixture
def categoria(db: None) -> Categoria:
    return Categoria.objects.create(nome="Alimentação")


@pytest.fixture
def fonte(db: None) -> Fonte:
    return Fonte.objects.create(nome="Salário")


@pytest.fixture
def gasto(db: None, categoria: Categoria) -> Gasto:
    return Gasto.objects.create(
        descricao="Supermercado",
        valor=Decimal("150.00"),
        categoria=categoria,
        data=date.today(),
    )


@pytest.fixture
def entrada(db: None, fonte: Fonte) -> Entrada:
    return Entrada.objects.create(
        descricao="Salário Janeiro",
        valor=Decimal("3000.00"),
        fonte=fonte,
        data=date.today(),
    )


# ---------------------------------------------------------------------------
# Autenticação — sem token deve retornar 401
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestAutenticacao:
    def test_categorias_sem_token_retorna_401(self, client: APIClient) -> None:
        response = client.get(reverse("categoria-list"))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_fontes_sem_token_retorna_401(self, client: APIClient) -> None:
        response = client.get(reverse("fonte-list"))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_gastos_sem_token_retorna_401(self, client: APIClient) -> None:
        response = client.get(reverse("gasto-list"))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_entradas_sem_token_retorna_401(self, client: APIClient) -> None:
        response = client.get(reverse("entrada-list"))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------------
# Categoria
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestCategoriaViewSet:
    def test_list(self, auth_client: APIClient, categoria: Categoria) -> None:
        response = auth_client.get(reverse("categoria-list"))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_create(self, auth_client: APIClient) -> None:
        response = auth_client.post(
            reverse("categoria-list"), {"nome": "Transporte"}
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert Categoria.objects.filter(nome="Transporte").exists()

    def test_retrieve(
        self, auth_client: APIClient, categoria: Categoria
    ) -> None:
        url = reverse("categoria-detail", args=[categoria.pk])
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["nome"] == "Alimentação"

    def test_update(
        self, auth_client: APIClient, categoria: Categoria
    ) -> None:
        url = reverse("categoria-detail", args=[categoria.pk])
        response = auth_client.put(url, {"nome": "Lazer"})
        assert response.status_code == status.HTTP_200_OK
        categoria.refresh_from_db()
        assert categoria.nome == "Lazer"

    def test_destroy(
        self, auth_client: APIClient, categoria: Categoria
    ) -> None:
        url = reverse("categoria-detail", args=[categoria.pk])
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Categoria.objects.filter(pk=categoria.pk).exists()

    def test_create_nome_duplicado_retorna_400(
        self, auth_client: APIClient, categoria: Categoria
    ) -> None:
        response = auth_client.post(
            reverse("categoria-list"), {"nome": "Alimentação"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ---------------------------------------------------------------------------
# Fonte
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestFonteViewSet:
    def test_list(self, auth_client: APIClient, fonte: Fonte) -> None:
        response = auth_client.get(reverse("fonte-list"))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_create(self, auth_client: APIClient) -> None:
        response = auth_client.post(
            reverse("fonte-list"), {"nome": "Freelance"}
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert Fonte.objects.filter(nome="Freelance").exists()

    def test_retrieve(self, auth_client: APIClient, fonte: Fonte) -> None:
        url = reverse("fonte-detail", args=[fonte.pk])
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["nome"] == "Salário"

    def test_update(self, auth_client: APIClient, fonte: Fonte) -> None:
        url = reverse("fonte-detail", args=[fonte.pk])
        response = auth_client.put(url, {"nome": "Bônus"})
        assert response.status_code == status.HTTP_200_OK
        fonte.refresh_from_db()
        assert fonte.nome == "Bônus"

    def test_destroy(self, auth_client: APIClient, fonte: Fonte) -> None:
        url = reverse("fonte-detail", args=[fonte.pk])
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Fonte.objects.filter(pk=fonte.pk).exists()

    def test_create_nome_duplicado_retorna_400(
        self, auth_client: APIClient, fonte: Fonte
    ) -> None:
        response = auth_client.post(reverse("fonte-list"), {"nome": "Salário"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ---------------------------------------------------------------------------
# Gasto
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestGastoViewSet:
    def test_list(self, auth_client: APIClient, gasto: Gasto) -> None:
        response = auth_client.get(reverse("gasto-list"))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_create(
        self, auth_client: APIClient, categoria: Categoria
    ) -> None:
        response = auth_client.post(
            reverse("gasto-list"),
            {
                "descricao": "Farmácia",
                "valor": "45.50",
                "categoria": categoria.pk,
                "data": date.today().isoformat(),
            },
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_retrieve(self, auth_client: APIClient, gasto: Gasto) -> None:
        url = reverse("gasto-detail", args=[gasto.pk])
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["descricao"] == "Supermercado"

    def test_update(
        self, auth_client: APIClient, gasto: Gasto, categoria: Categoria
    ) -> None:
        url = reverse("gasto-detail", args=[gasto.pk])
        response = auth_client.put(
            url,
            {
                "descricao": "Mercado",
                "valor": "200.00",
                "categoria": categoria.pk,
                "data": date.today().isoformat(),
            },
        )
        assert response.status_code == status.HTTP_200_OK
        gasto.refresh_from_db()
        assert gasto.descricao == "Mercado"

    def test_destroy(self, auth_client: APIClient, gasto: Gasto) -> None:
        url = reverse("gasto-detail", args=[gasto.pk])
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Gasto.objects.filter(pk=gasto.pk).exists()

    def test_create_valor_negativo_retorna_400(
        self, auth_client: APIClient, categoria: Categoria
    ) -> None:
        response = auth_client.post(
            reverse("gasto-list"),
            {
                "descricao": "Inválido",
                "valor": "-10.00",
                "categoria": categoria.pk,
                "data": date.today().isoformat(),
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_valor_zero_retorna_400(
        self, auth_client: APIClient, categoria: Categoria
    ) -> None:
        response = auth_client.post(
            reverse("gasto-list"),
            {
                "descricao": "Inválido",
                "valor": "0.00",
                "categoria": categoria.pk,
                "data": date.today().isoformat(),
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_sem_descricao_retorna_400(
        self, auth_client: APIClient, categoria: Categoria
    ) -> None:
        response = auth_client.post(
            reverse("gasto-list"),
            {
                "valor": "50.00",
                "categoria": categoria.pk,
                "data": date.today().isoformat(),
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_sem_categoria_retorna_400(
        self, auth_client: APIClient
    ) -> None:
        response = auth_client.post(
            reverse("gasto-list"),
            {
                "descricao": "Sem categoria",
                "valor": "50.00",
                "data": date.today().isoformat(),
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_data_invalida_retorna_400(
        self, auth_client: APIClient, categoria: Categoria
    ) -> None:
        response = auth_client.post(
            reverse("gasto-list"),
            {
                "descricao": "Data inválida",
                "valor": "50.00",
                "categoria": categoria.pk,
                "data": "nao-e-uma-data",
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_patch_valor(self, auth_client: APIClient, gasto: Gasto) -> None:
        url = reverse("gasto-detail", args=[gasto.pk])
        response = auth_client.patch(url, {"valor": "99.99"})
        assert response.status_code == status.HTTP_200_OK
        gasto.refresh_from_db()
        assert gasto.valor == Decimal("99.99")

    def test_patch_descricao(
        self, auth_client: APIClient, gasto: Gasto
    ) -> None:
        url = reverse("gasto-detail", args=[gasto.pk])
        response = auth_client.patch(url, {"descricao": "Padaria"})
        assert response.status_code == status.HTTP_200_OK
        gasto.refresh_from_db()
        assert gasto.descricao == "Padaria"

    def test_criado_em_ignorado_no_create(
        self, auth_client: APIClient, categoria: Categoria
    ) -> None:
        # criado_em é auto_now_add — deve ser ignorado mesmo se enviado.
        response = auth_client.post(
            reverse("gasto-list"),
            {
                "descricao": "Teste",
                "valor": "10.00",
                "categoria": categoria.pk,
                "data": date.today().isoformat(),
                "criado_em": "2000-01-01T00:00:00Z",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        gasto = Gasto.objects.get(pk=response.data["id"])
        assert gasto.criado_em.year != 2000


# ---------------------------------------------------------------------------
# Entrada
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestEntradaViewSet:
    def test_list(self, auth_client: APIClient, entrada: Entrada) -> None:
        response = auth_client.get(reverse("entrada-list"))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_create(self, auth_client: APIClient, fonte: Fonte) -> None:
        response = auth_client.post(
            reverse("entrada-list"),
            {
                "descricao": "Freelance",
                "valor": "500.00",
                "fonte": fonte.pk,
                "data": date.today().isoformat(),
            },
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_retrieve(self, auth_client: APIClient, entrada: Entrada) -> None:
        url = reverse("entrada-detail", args=[entrada.pk])
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["descricao"] == "Salário Janeiro"

    def test_update(
        self, auth_client: APIClient, entrada: Entrada, fonte: Fonte
    ) -> None:
        url = reverse("entrada-detail", args=[entrada.pk])
        response = auth_client.put(
            url,
            {
                "descricao": "Salário Fevereiro",
                "valor": "3200.00",
                "fonte": fonte.pk,
                "data": date.today().isoformat(),
            },
        )
        assert response.status_code == status.HTTP_200_OK
        entrada.refresh_from_db()
        assert entrada.descricao == "Salário Fevereiro"

    def test_destroy(self, auth_client: APIClient, entrada: Entrada) -> None:
        url = reverse("entrada-detail", args=[entrada.pk])
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Entrada.objects.filter(pk=entrada.pk).exists()

    def test_create_valor_negativo_retorna_400(
        self, auth_client: APIClient, fonte: Fonte
    ) -> None:
        response = auth_client.post(
            reverse("entrada-list"),
            {
                "descricao": "Inválido",
                "valor": "-10.00",
                "fonte": fonte.pk,
                "data": date.today().isoformat(),
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_valor_zero_retorna_400(
        self, auth_client: APIClient, fonte: Fonte
    ) -> None:
        response = auth_client.post(
            reverse("entrada-list"),
            {
                "descricao": "Inválido",
                "valor": "0.00",
                "fonte": fonte.pk,
                "data": date.today().isoformat(),
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_sem_descricao_retorna_400(
        self, auth_client: APIClient, fonte: Fonte
    ) -> None:
        response = auth_client.post(
            reverse("entrada-list"),
            {
                "valor": "500.00",
                "fonte": fonte.pk,
                "data": date.today().isoformat(),
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_sem_fonte_retorna_400(
        self, auth_client: APIClient
    ) -> None:
        response = auth_client.post(
            reverse("entrada-list"),
            {
                "descricao": "Sem fonte",
                "valor": "500.00",
                "data": date.today().isoformat(),
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_data_invalida_retorna_400(
        self, auth_client: APIClient, fonte: Fonte
    ) -> None:
        response = auth_client.post(
            reverse("entrada-list"),
            {
                "descricao": "Data inválida",
                "valor": "500.00",
                "fonte": fonte.pk,
                "data": "nao-e-uma-data",
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_patch_valor(
        self, auth_client: APIClient, entrada: Entrada
    ) -> None:
        url = reverse("entrada-detail", args=[entrada.pk])
        response = auth_client.patch(url, {"valor": "3500.00"})
        assert response.status_code == status.HTTP_200_OK
        entrada.refresh_from_db()
        assert entrada.valor == Decimal("3500.00")

    def test_patch_descricao(
        self, auth_client: APIClient, entrada: Entrada
    ) -> None:
        url = reverse("entrada-detail", args=[entrada.pk])
        response = auth_client.patch(url, {"descricao": "Salário Março"})
        assert response.status_code == status.HTTP_200_OK
        entrada.refresh_from_db()
        assert entrada.descricao == "Salário Março"

    def test_criado_em_ignorado_no_create(
        self, auth_client: APIClient, fonte: Fonte
    ) -> None:
        # criado_em é auto_now_add — deve ser ignorado mesmo se enviado.
        response = auth_client.post(
            reverse("entrada-list"),
            {
                "descricao": "Teste",
                "valor": "100.00",
                "fonte": fonte.pk,
                "data": date.today().isoformat(),
                "criado_em": "2000-01-01T00:00:00Z",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        entrada = Entrada.objects.get(pk=response.data["id"])
        assert entrada.criado_em.year != 2000


# ---------------------------------------------------------------------------
# Filtros — Gasto
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestGastoFiltros:
    def test_filtro_por_categoria(
        self, auth_client: APIClient, categoria: Categoria
    ) -> None:
        # Cria um gasto na categoria fixture e outro em categoria diferente.
        Gasto.objects.create(
            descricao="A",
            valor=Decimal("10.00"),
            categoria=categoria,
            data=date.today(),
        )
        outra = Categoria.objects.create(nome="Outra")
        Gasto.objects.create(
            descricao="B",
            valor=Decimal("20.00"),
            categoria=outra,
            data=date.today(),
        )
        url = reverse("gasto-list") + f"?categoria={categoria.pk}"
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_filtro_por_data_gte(
        self, auth_client: APIClient, categoria: Categoria
    ) -> None:
        hoje = date.today()
        ontem = hoje - timedelta(days=1)
        Gasto.objects.create(
            descricao="Hoje",
            valor=Decimal("10.00"),
            categoria=categoria,
            data=hoje,
        )
        Gasto.objects.create(
            descricao="Ontem",
            valor=Decimal("10.00"),
            categoria=categoria,
            data=ontem,
        )
        url = reverse("gasto-list") + f"?data__gte={hoje.isoformat()}"
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_filtro_por_valor_lte(
        self, auth_client: APIClient, categoria: Categoria
    ) -> None:
        Gasto.objects.create(
            descricao="Barato",
            valor=Decimal("10.00"),
            categoria=categoria,
            data=date.today(),
        )
        Gasto.objects.create(
            descricao="Caro",
            valor=Decimal("500.00"),
            categoria=categoria,
            data=date.today(),
        )
        url = reverse("gasto-list") + "?valor__lte=100"
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1


# ---------------------------------------------------------------------------
# Filtros — Entrada
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestEntradaFiltros:
    def test_filtro_por_fonte(
        self, auth_client: APIClient, fonte: Fonte
    ) -> None:
        Entrada.objects.create(
            descricao="A",
            valor=Decimal("100.00"),
            fonte=fonte,
            data=date.today(),
        )
        outra = Fonte.objects.create(nome="Outra")
        Entrada.objects.create(
            descricao="B",
            valor=Decimal("200.00"),
            fonte=outra,
            data=date.today(),
        )
        url = reverse("entrada-list") + f"?fonte={fonte.pk}"
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_filtro_por_valor_gte(
        self, auth_client: APIClient, fonte: Fonte
    ) -> None:
        Entrada.objects.create(
            descricao="Pequena",
            valor=Decimal("50.00"),
            fonte=fonte,
            data=date.today(),
        )
        Entrada.objects.create(
            descricao="Grande",
            valor=Decimal("5000.00"),
            fonte=fonte,
            data=date.today(),
        )
        url = reverse("entrada-list") + "?valor__gte=1000"
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1


# ---------------------------------------------------------------------------
# Paginação
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestPaginacao:
    def test_resposta_paginada_tem_estrutura_correta(
        self, auth_client: APIClient, categoria: Categoria
    ) -> None:
        # Cria 1 gasto e verifica que a resposta tem campos de paginação.
        Gasto.objects.create(
            descricao="Teste",
            valor=Decimal("10.00"),
            categoria=categoria,
            data=date.today(),
        )
        response = auth_client.get(reverse("gasto-list"))
        assert response.status_code == status.HTTP_200_OK
        assert "count" in response.data
        assert "next" in response.data
        assert "previous" in response.data
        assert "results" in response.data

    def test_count_reflete_total_de_registros(
        self, auth_client: APIClient, categoria: Categoria
    ) -> None:
        for i in range(3):
            Gasto.objects.create(
                descricao=f"Gasto {i}",
                valor=Decimal("10.00"),
                categoria=categoria,
                data=date.today(),
            )
        response = auth_client.get(reverse("gasto-list"))
        assert response.data["count"] == 3


# ---------------------------------------------------------------------------
# Resumo financeiro
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestResumo:
    def test_resumo_sem_dados_retorna_zeros(
        self, auth_client: APIClient
    ) -> None:
        response = auth_client.get(reverse("resumo"))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["total_entradas"] == 0
        assert response.data["total_gastos"] == 0
        assert response.data["saldo"] == 0

    def test_resumo_calcula_saldo(
        self,
        auth_client: APIClient,
        categoria: Categoria,
        fonte: Fonte,
    ) -> None:
        Entrada.objects.create(
            descricao="Salário",
            valor=Decimal("3000.00"),
            fonte=fonte,
            data=date.today(),
        )
        Gasto.objects.create(
            descricao="Aluguel",
            valor=Decimal("1000.00"),
            categoria=categoria,
            data=date.today(),
        )
        response = auth_client.get(reverse("resumo"))
        assert response.data["total_entradas"] == Decimal("3000.00")
        assert response.data["total_gastos"] == Decimal("1000.00")
        assert response.data["saldo"] == Decimal("2000.00")

    def test_resumo_agrupa_gastos_por_categoria(
        self,
        auth_client: APIClient,
        categoria: Categoria,
    ) -> None:
        outra = Categoria.objects.create(nome="Transporte")
        Gasto.objects.create(
            descricao="Mercado",
            valor=Decimal("200.00"),
            categoria=categoria,
            data=date.today(),
        )
        Gasto.objects.create(
            descricao="Uber",
            valor=Decimal("50.00"),
            categoria=outra,
            data=date.today(),
        )
        response = auth_client.get(reverse("resumo"))
        por_categoria = {
            item["categoria__nome"]: item["total"]
            for item in response.data["gastos_por_categoria"]
        }
        assert por_categoria["Alimentação"] == Decimal("200.00")
        assert por_categoria["Transporte"] == Decimal("50.00")

    def test_resumo_sem_token_retorna_401(self, client: APIClient) -> None:
        response = client.get(reverse("resumo"))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
