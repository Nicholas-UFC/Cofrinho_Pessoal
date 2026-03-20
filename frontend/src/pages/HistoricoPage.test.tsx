import { describe, it, expect } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { renderWithProviders } from "../test/utils";
import { makeFakeToken } from "../test/handlers";
import { server } from "../test/server";
import HistoricoPage from "./HistoricoPage";

describe("HistoricoPage — lista de gastos", () => {
    it("exibe os gastos carregados da API", async () => {
        localStorage.setItem("access", makeFakeToken());
        renderWithProviders(<HistoricoPage />);
        await waitFor(() => {
            expect(screen.getByText("Mercado")).toBeInTheDocument();
            expect(screen.getByText("Uber")).toBeInTheDocument();
        });
    });

    it("exibe o nome da categoria do gasto", async () => {
        localStorage.setItem("access", makeFakeToken());
        renderWithProviders(<HistoricoPage />);
        await waitFor(() => {
            expect(screen.getByText("Alimentação")).toBeInTheDocument();
            expect(screen.getByText("Transporte")).toBeInTheDocument();
        });
    });

    it("exibe os valores formatados em BRL", async () => {
        localStorage.setItem("access", makeFakeToken());
        renderWithProviders(<HistoricoPage />);
        await waitFor(() => {
            expect(screen.getByText("R$ 50,00")).toBeInTheDocument();
            expect(screen.getByText("R$ 25,00")).toBeInTheDocument();
        });
    });

    it("exibe a contagem total de registros", async () => {
        localStorage.setItem("access", makeFakeToken());
        renderWithProviders(<HistoricoPage />);
        await waitFor(() => {
            expect(screen.getByText(/2 registros/)).toBeInTheDocument();
        });
    });
});

describe("HistoricoPage — alternância de abas", () => {
    it("clicar em Entradas exibe os dados de entradas", async () => {
        localStorage.setItem("access", makeFakeToken());
        renderWithProviders(<HistoricoPage />);
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
        renderWithProviders(<HistoricoPage />);
        await userEvent.click(screen.getByText(/Entradas/));
        await waitFor(() => {
            const valorEl = screen.getByText("R$ 3.000,00");
            expect(valorEl).toHaveStyle({ color: "#22c55e" });
        });
    });
});

describe("HistoricoPage — paginação", () => {
    it("botão Anterior está desabilitado na primeira página", async () => {
        localStorage.setItem("access", makeFakeToken());
        renderWithProviders(<HistoricoPage />);
        await waitFor(() => {
            expect(screen.getByText("Mercado")).toBeInTheDocument();
        });
        const anterior = screen.getByText(/Anterior/);
        expect(anterior).toBeDisabled();
    });

    it("botão Próxima está desabilitado quando não há próxima página", async () => {
        localStorage.setItem("access", makeFakeToken());
        renderWithProviders(<HistoricoPage />);
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
        renderWithProviders(<HistoricoPage />);
        await waitFor(() => {
            expect(screen.getByText("Mercado")).toBeInTheDocument();
        });
        const proxima = screen.getByText(/Próxima/);
        expect(proxima).not.toBeDisabled();
    });
});

describe("HistoricoPage — estado vazio", () => {
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
        renderWithProviders(<HistoricoPage />);
        await waitFor(() => {
            expect(
                screen.getByText("Nenhum registro encontrado."),
            ).toBeInTheDocument();
        });
    });
});

describe("HistoricoPage — erro de API", () => {
    it("exibe mensagem de erro quando a API falha", async () => {
        server.use(
            http.get("http://localhost:8000/api/financas/gastos/", () =>
                HttpResponse.json({ detail: "Server Error" }, { status: 500 }),
            ),
        );

        localStorage.setItem("access", makeFakeToken());
        renderWithProviders(<HistoricoPage />);
        await waitFor(() => {
            expect(
                screen.getByText("Erro ao carregar histórico."),
            ).toBeInTheDocument();
        });
    });
});
