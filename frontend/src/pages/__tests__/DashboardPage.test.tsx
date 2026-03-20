import { describe, it, expect } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { renderWithProviders } from "../../test/utils";
import { server } from "../../test/server";
import DashboardPage from "../DashboardPage";

describe("DashboardPage", () => {
    it("exibe estado de carregamento inicialmente", () => {
        renderWithProviders(<DashboardPage />);
        expect(screen.getByText(/carregando/i)).toBeInTheDocument();
    });

    it("exibe os três cards de resumo financeiro", async () => {
        renderWithProviders(<DashboardPage />);
        await waitFor(() => {
            expect(screen.getByText("Total de Entradas")).toBeInTheDocument();
        });
        expect(screen.getByText("Total de Gastos")).toBeInTheDocument();
        expect(screen.getByText("Saldo")).toBeInTheDocument();
    });

    it("exibe os valores do resumo em formato monetário BRL", async () => {
        renderWithProviders(<DashboardPage />);
        await waitFor(() => {
            expect(screen.getByText(/1\.500,00/)).toBeInTheDocument();
        });
        expect(screen.getByText(/800,00/)).toBeInTheDocument();
        expect(screen.getByText(/700,00/)).toBeInTheDocument();
    });

    it("exibe mensagem de erro quando a API falha", async () => {
        server.use(
            http.get("http://localhost:8000/api/financas/resumo/", () =>
                HttpResponse.json({ detail: "Erro interno" }, { status: 500 }),
            ),
        );
        renderWithProviders(<DashboardPage />);
        await waitFor(() => {
            expect(
                screen.getByText(/erro ao carregar resumo/i),
            ).toBeInTheDocument();
        });
    });

    it("saldo negativo exibe com cor vermelha", async () => {
        server.use(
            http.get("http://localhost:8000/api/financas/resumo/", () =>
                HttpResponse.json({
                    total_entradas: "500.00",
                    total_gastos: "800.00",
                    saldo: "-300.00",
                }),
            ),
        );
        renderWithProviders(<DashboardPage />);
        await waitFor(() => {
            expect(screen.getByText("Saldo")).toBeInTheDocument();
        });
        // Encontra o elemento que exibe o valor do saldo (negativo)
        const saldoEl = screen.getByText(/300,00/);
        expect(saldoEl).toHaveStyle({ color: "#f87171" });
    });
});
