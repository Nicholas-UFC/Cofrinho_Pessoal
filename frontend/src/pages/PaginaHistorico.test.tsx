import { describe, it, expect } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { renderWithProviders } from "../test/utils";
import { makeFakeToken } from "../test/handlers";
import { server } from "../test/server";
import PaginaHistorico from "./PaginaHistorico";

/*
 * PaginaHistorico — testes de exibição, abas, paginação e erros
 * --------------------------------------------------------------
 *
 * A PaginaHistorico exibe o histórico financeiro do usuário em duas
 * abas: Gastos e Entradas. Cada aba busca os dados do endpoint
 * correspondente, formata os valores em BRL e exibe a categoria/fonte
 * de cada registro.
 *
 * Os testes são divididos em cinco grupos:
 *
 * 1. LISTA DE GASTOS: verifica que os dados chegam corretamente da API
 *    e são exibidos — descrição, categoria, valor formatado em BRL e
 *    contagem total de registros.
 *
 * 2. ALTERNÂNCIA DE ABAS: clicar em "Entradas" substitui a lista de
 *    gastos pela lista de entradas. Entradas devem aparecer em verde
 *    para sinalizar que são receitas, não despesas.
 *
 * 3. PAGINAÇÃO: os botões Anterior e Próxima refletem corretamente o
 *    estado da paginação — desabilitados quando não há mais páginas,
 *    habilitados quando o campo `next` da API não é nulo.
 *
 * 4. ESTADO VAZIO: quando a API retorna uma lista vazia, a tela exibe
 *    uma mensagem amigável em vez de uma tabela vazia sem contexto.
 *
 * 5. ERRO DE API: quando o endpoint falha com 500, a tela exibe uma
 *    mensagem de erro clara para o usuário.
 */

describe("PaginaHistorico — lista de gastos", () => {
    it("exibe os gastos carregados da API", async () => {
        localStorage.setItem("access", makeFakeToken());
        renderWithProviders(<PaginaHistorico />);
        await waitFor(() => {
            expect(screen.getByText("Mercado")).toBeInTheDocument();
            expect(screen.getByText("Uber")).toBeInTheDocument();
        });
    });

    it("exibe o nome da categoria do gasto", async () => {
        localStorage.setItem("access", makeFakeToken());
        renderWithProviders(<PaginaHistorico />);
        await waitFor(() => {
            expect(screen.getByText("Alimentação")).toBeInTheDocument();
            expect(screen.getByText("Transporte")).toBeInTheDocument();
        });
    });

    it("exibe os valores formatados em BRL", async () => {
        localStorage.setItem("access", makeFakeToken());
        renderWithProviders(<PaginaHistorico />);
        await waitFor(() => {
            expect(screen.getByText("R$ 50,00")).toBeInTheDocument();
            expect(screen.getByText("R$ 25,00")).toBeInTheDocument();
        });
    });

    it("exibe a contagem total de registros", async () => {
        localStorage.setItem("access", makeFakeToken());
        renderWithProviders(<PaginaHistorico />);
        await waitFor(() => {
            expect(screen.getByText(/2 registros/)).toBeInTheDocument();
        });
    });
});

describe("PaginaHistorico — alternância de abas", () => {
    it("clicar em Entradas exibe os dados de entradas", async () => {
        localStorage.setItem("access", makeFakeToken());
        renderWithProviders(<PaginaHistorico />);
        await waitFor(() => {
            expect(screen.getByText("Mercado")).toBeInTheDocument();
        });
        await userEvent.click(screen.getByText(/Entradas/));
        await waitFor(() => {
            expect(screen.getByText("Salário")).toBeInTheDocument();
            expect(screen.getByText("Nubank")).toBeInTheDocument();
        });
    });

    it("entradas exibem valores em verde", async () => {
        localStorage.setItem("access", makeFakeToken());
        renderWithProviders(<PaginaHistorico />);
        await userEvent.click(screen.getByText(/Entradas/));
        await waitFor(() => {
            const valorEl = screen.getByText("R$ 3.000,00");
            expect(valorEl).toHaveStyle({ color: "#22c55e" });
        });
    });
});

describe("PaginaHistorico — paginação", () => {
    it("botão Anterior está desabilitado na primeira página", async () => {
        localStorage.setItem("access", makeFakeToken());
        renderWithProviders(<PaginaHistorico />);
        await waitFor(() => {
            expect(screen.getByText("Mercado")).toBeInTheDocument();
        });
        const anterior = screen.getByText(/Anterior/);
        expect(anterior).toBeDisabled();
    });

    it("botão Próxima está desabilitado quando não há próxima página", async () => {
        localStorage.setItem("access", makeFakeToken());
        renderWithProviders(<PaginaHistorico />);
        await waitFor(() => {
            expect(screen.getByText("Mercado")).toBeInTheDocument();
        });
        const proxima = screen.getByText(/Próxima/);
        expect(proxima).toBeDisabled();
    });

    it("botão Próxima está habilitado quando existe próxima página", async () => {
        server.use(
            http.get("http://localhost:8000/api/financas/gastos/", () =>
                HttpResponse.json({
                    count: 20,
                    next: "http://localhost:8000/api/financas/gastos/?page=2",
                    previous: null,
                    results: [
                        {
                            id: 1,
                            descricao: "Mercado",
                            valor: "50.00",
                            data: "2026-03-01",
                            categoria: 1,
                            categoria_nome: "Alimentação",
                        },
                    ],
                }),
            ),
        );

        localStorage.setItem("access", makeFakeToken());
        renderWithProviders(<PaginaHistorico />);
        await waitFor(() => {
            expect(screen.getByText("Mercado")).toBeInTheDocument();
        });
        const proxima = screen.getByText(/Próxima/);
        expect(proxima).not.toBeDisabled();
    });
});

describe("PaginaHistorico — estado vazio", () => {
    it("exibe mensagem quando não há registros", async () => {
        server.use(
            http.get("http://localhost:8000/api/financas/gastos/", () =>
                HttpResponse.json({
                    count: 0,
                    next: null,
                    previous: null,
                    results: [],
                }),
            ),
        );

        localStorage.setItem("access", makeFakeToken());
        renderWithProviders(<PaginaHistorico />);
        await waitFor(() => {
            expect(
                screen.getByText("Nenhum registro encontrado."),
            ).toBeInTheDocument();
        });
    });
});

describe("PaginaHistorico — erro de API", () => {
    it("exibe mensagem de erro quando a API falha", async () => {
        server.use(
            http.get("http://localhost:8000/api/financas/gastos/", () =>
                HttpResponse.json({ detail: "Server Error" }, { status: 500 }),
            ),
        );

        localStorage.setItem("access", makeFakeToken());
        renderWithProviders(<PaginaHistorico />);
        await waitFor(() => {
            expect(
                screen.getByText("Erro ao carregar histórico."),
            ).toBeInTheDocument();
        });
    });
});
