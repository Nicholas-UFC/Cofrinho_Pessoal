import { describe, it, expect } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { renderWithProviders } from "../../test/utils";
import { server } from "../../test/server";
import HistoricoPage from "../HistoricoPage";

describe("HistoricoPage", () => {
    it("exibe estado de carregamento inicialmente", () => {
        renderWithProviders(<HistoricoPage />);
        expect(screen.getByText(/carregando/i)).toBeInTheDocument();
    });

    it("exibe a lista de gastos por padrão", async () => {
        renderWithProviders(<HistoricoPage />);
        await waitFor(() => {
            expect(screen.getByText("Mercado")).toBeInTheDocument();
        });
        expect(screen.getByText("Alimentação")).toBeInTheDocument();
        expect(screen.getByText("Uber")).toBeInTheDocument();
        expect(screen.getByText("Transporte")).toBeInTheDocument();
    });

    it("exibe valores de gastos formatados em BRL", async () => {
        renderWithProviders(<HistoricoPage />);
        await waitFor(() => {
            expect(screen.getByText("Mercado")).toBeInTheDocument();
        });
        expect(screen.getByText(/50,00/)).toBeInTheDocument();
        expect(screen.getByText(/25,00/)).toBeInTheDocument();
    });

    it("troca para a view de entradas ao clicar na aba", async () => {
        renderWithProviders(<HistoricoPage />);
        await waitFor(() => {
            expect(screen.getByText("Mercado")).toBeInTheDocument();
        });
        await userEvent.click(
            screen.getByRole("button", { name: /entradas/i }),
        );
        await waitFor(() => {
            expect(screen.getByText("Salário")).toBeInTheDocument();
        });
        expect(screen.getByText("Nubank")).toBeInTheDocument();
    });

    it("desabilita botão Anterior na primeira página", async () => {
        renderWithProviders(<HistoricoPage />);
        await waitFor(() => {
            expect(screen.getByText("Mercado")).toBeInTheDocument();
        });
        expect(
            screen.getByRole("button", { name: /anterior/i }),
        ).toBeDisabled();
    });

    it("desabilita botão Próxima quando não há próxima página", async () => {
        renderWithProviders(<HistoricoPage />);
        await waitFor(() => {
            expect(screen.getByText("Mercado")).toBeInTheDocument();
        });
        expect(
            screen.getByRole("button", { name: /próxima/i }),
        ).toBeDisabled();
    });

    it("habilita botão Próxima quando há próxima página", async () => {
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
        renderWithProviders(<HistoricoPage />);
        await waitFor(() => {
            expect(screen.getByText("Mercado")).toBeInTheDocument();
        });
        expect(
            screen.getByRole("button", { name: /próxima/i }),
        ).not.toBeDisabled();
    });

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
        renderWithProviders(<HistoricoPage />);
        await waitFor(() => {
            expect(
                screen.getByText(/nenhum registro encontrado/i),
            ).toBeInTheDocument();
        });
    });

    it("exibe erro quando a API falha", async () => {
        server.use(
            http.get("http://localhost:8000/api/financas/gastos/", () =>
                HttpResponse.json({ detail: "Erro" }, { status: 500 }),
            ),
        );
        renderWithProviders(<HistoricoPage />);
        await waitFor(() => {
            expect(
                screen.getByText(/erro ao carregar histórico/i),
            ).toBeInTheDocument();
        });
    });
});
