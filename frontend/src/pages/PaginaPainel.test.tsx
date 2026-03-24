import { describe, it, expect } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { renderWithProviders } from "../test/utils";
import { makeFakeToken } from "../test/handlers";
import { server } from "../test/server";
import PaginaPainel from "./PaginaPainel";

describe("PaginaPainel — carregamento", () => {
    it("exibe 'Carregando...' antes dos dados chegarem", () => {
        localStorage.setItem("access", makeFakeToken());
        renderWithProviders(<PaginaPainel />);
        expect(screen.getByText("Carregando...")).toBeInTheDocument();
    });

    it("exibe os 3 cards após carregar os dados", async () => {
        localStorage.setItem("access", makeFakeToken());
        renderWithProviders(<PaginaPainel />);
        await waitFor(() => {
            expect(screen.getByText("Total de Entradas")).toBeInTheDocument();
            expect(screen.getByText("Total de Gastos")).toBeInTheDocument();
            expect(screen.getByText("Saldo")).toBeInTheDocument();
        });
    });

    it("exibe os valores formatados em BRL", async () => {
        localStorage.setItem("access", makeFakeToken());
        renderWithProviders(<PaginaPainel />);
        await waitFor(() => {
            expect(screen.getByText("R$ 1.500,00")).toBeInTheDocument();
            expect(screen.getByText("R$ 800,00")).toBeInTheDocument();
            expect(screen.getByText("R$ 700,00")).toBeInTheDocument();
        });
    });
});

describe("PaginaPainel — cores do saldo", () => {
    it("saldo positivo é exibido em verde", async () => {
        localStorage.setItem("access", makeFakeToken());
        renderWithProviders(<PaginaPainel />);
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
        renderWithProviders(<PaginaPainel />);
        await waitFor(() => {
            expect(screen.getByText("-R$ 300,00")).toBeInTheDocument();
        });
        const saldoEl = screen.getByText("-R$ 300,00");
        expect(saldoEl).toHaveStyle({ color: "#f87171" });
    });
});

describe("PaginaPainel — erro de API", () => {
    it("exibe mensagem de erro quando a API falha", async () => {
        server.use(
            http.get("http://localhost:8000/api/financas/resumo/", () =>
                HttpResponse.json({ detail: "Server Error" }, { status: 500 }),
            ),
        );

        localStorage.setItem("access", makeFakeToken());
        renderWithProviders(<PaginaPainel />);
        await waitFor(() => {
            expect(
                screen.getByText("Erro ao carregar dados do dashboard."),
            ).toBeInTheDocument();
        });
    });
});

describe("PaginaPainel — gráficos", () => {
    it("exibe o título dos 4 gráficos", async () => {
        localStorage.setItem("access", makeFakeToken());
        renderWithProviders(<PaginaPainel />);
        await waitFor(() => {
            expect(screen.getByText("Entradas vs Gastos")).toBeInTheDocument();
            expect(
                screen.getByText("Linha do Tempo — Últimos 3 Meses"),
            ).toBeInTheDocument();
            expect(
                screen.getByText("Gastos por Categoria"),
            ).toBeInTheDocument();
            expect(screen.getByText("Entradas por Fonte")).toBeInTheDocument();
        });
    });

    it("exibe mensagem vazia quando não há gastos", async () => {
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
        renderWithProviders(<PaginaPainel />);
        await waitFor(() => {
            expect(
                screen.getByText("Nenhum gasto registrado."),
            ).toBeInTheDocument();
        });
    });

    it("exibe mensagem vazia quando não há entradas", async () => {
        server.use(
            http.get("http://localhost:8000/api/financas/entradas/", () =>
                HttpResponse.json({
                    count: 0,
                    next: null,
                    previous: null,
                    results: [],
                }),
            ),
        );

        localStorage.setItem("access", makeFakeToken());
        renderWithProviders(<PaginaPainel />);
        await waitFor(() => {
            expect(
                screen.getByText("Nenhuma entrada registrada."),
            ).toBeInTheDocument();
        });
    });
});
