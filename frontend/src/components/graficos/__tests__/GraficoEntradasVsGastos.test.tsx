import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { GraficoEntradasVsGastos } from "../GraficoEntradasVsGastos";

vi.mock("recharts", async () => {
    const React = await import("react");
    return {
        ResponsiveContainer: ({ children }: { children: React.ReactNode }) =>
            React.createElement(React.Fragment, null, children),
        BarChart: ({ children }: { children: React.ReactNode }) =>
            React.createElement(
                "div",
                { "data-testid": "bar-chart" },
                children,
            ),
        Bar: () => null,
        XAxis: () => null,
        YAxis: () => null,
        CartesianGrid: () => null,
        Tooltip: () => null,
        Legend: () => null,
    };
});

// ---------------------------------------------------------------------------
// GraficoEntradasVsGastos
// ---------------------------------------------------------------------------

describe("GraficoEntradasVsGastos", () => {
    it("renderiza o título 'Entradas vs Gastos'", () => {
        render(
            <GraficoEntradasVsGastos totalEntradas={1500} totalGastos={800} />,
        );
        expect(screen.getByText("Entradas vs Gastos")).toBeInTheDocument();
    });

    it("renderiza o gráfico de barras", () => {
        render(
            <GraficoEntradasVsGastos totalEntradas={1500} totalGastos={800} />,
        );
        expect(screen.getByTestId("bar-chart")).toBeInTheDocument();
    });

    it("renderiza sem erros com valores zerados", () => {
        expect(() =>
            render(
                <GraficoEntradasVsGastos totalEntradas={0} totalGastos={0} />,
            ),
        ).not.toThrow();
    });

    it("renderiza sem erros com saldo negativo", () => {
        expect(() =>
            render(
                <GraficoEntradasVsGastos
                    totalEntradas={100}
                    totalGastos={500}
                />,
            ),
        ).not.toThrow();
    });

    it("renderiza sem erros com valores altos", () => {
        expect(() =>
            render(
                <GraficoEntradasVsGastos
                    totalEntradas={999999}
                    totalGastos={888888}
                />,
            ),
        ).not.toThrow();
    });
});
