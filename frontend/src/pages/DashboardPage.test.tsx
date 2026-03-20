import { describe, it, expect } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { renderWithProviders } from "../test/utils";
import { makeFakeToken } from "../test/handlers";
import { server } from "../test/server";
import DashboardPage from "./DashboardPage";

describe("DashboardPage — carregamento", () => {
    it("exibe 'Carregando...' antes dos dados chegarem", () => {
        localStorage.setItem("access", makeFakeToken());
        renderWithProviders(<DashboardPage />);
        expect(screen.getByText("Carregando...")).toBeInTheDocument();
    });

    it("exibe os 3 cards após carregar os dados", async () => {
        localStorage.setItem("access", makeFakeToken());
        renderWithProviders(<DashboardPage />);
        await waitFor(() => {
            expect(screen.getByText("Total de Entradas")).toBeInTheDocument();
            expect(screen.getByText("Total de Gastos")).toBeInTheDocument();
            expect(screen.getByText("Saldo")).toBeInTheDocument();
        });
    });

    it("exibe os valores formatados em BRL", async () => {
        localStorage.setItem("access", makeFakeToken());
        renderWithProviders(<DashboardPage />);
        await waitFor(() => {
            expect(screen.getByText("R$ 1.500,00")).toBeInTheDocument();
            expect(screen.getByText("R$ 800,00")).toBeInTheDocument();
            expect(screen.getByText("R$ 700,00")).toBeInTheDocument();
        });
    });
});

describe("DashboardPage — cores do saldo", () => {
    it("saldo positivo é exibido em verde", async () => {
        localStorage.setItem("access", makeFakeToken());
        renderWithProviders(<DashboardPage />);
        await waitFor(() => {
            expect(screen.getByText("R$ 700,00")).toBeInTheDocument();
        });
        const saldoEl = screen.getByText("R$ 700,00");
        expect(saldoEl).toHaveStyle({ color: "#22c55e" });
    });

    it("saldo negativo é exibido em vermelho", async () => {
        server.use(
            http.get("http://localhost:8000/api/financas/resumo/", () =>
                HttpResponse.json({
                    total_entradas: "500.00",
                    total_gastos: "800.00",
                    saldo: "-300.00",
                }),
            ),
        );

        localStorage.setItem("access", makeFakeToken());
        renderWithProviders(<DashboardPage />);
        await waitFor(() => {
            expect(screen.getByText("-R$ 300,00")).toBeInTheDocument();
        });
        const saldoEl = screen.getByText("-R$ 300,00");
        expect(saldoEl).toHaveStyle({ color: "#f87171" });
    });
});

describe("DashboardPage — erro de API", () => {
    it("exibe mensagem de erro quando a API falha", async () => {
        server.use(
            http.get("http://localhost:8000/api/financas/resumo/", () =>
                HttpResponse.json({ detail: "Server Error" }, { status: 500 }),
            ),
        );

        localStorage.setItem("access", makeFakeToken());
        renderWithProviders(<DashboardPage />);
        await waitFor(() => {
            expect(
                screen.getByText("Erro ao carregar resumo financeiro."),
            ).toBeInTheDocument();
        });
    });
});
