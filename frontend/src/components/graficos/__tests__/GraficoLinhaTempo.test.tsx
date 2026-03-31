import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { GraficoLinhaTempo } from "../GraficoLinhaTempo";
import type { MonthPoint } from "../../../utils/graficos";

vi.mock("recharts", async () => {
    const React = await import("react");
    return {
        ResponsiveContainer: ({ children }: { children: React.ReactNode }) =>
            React.createElement(React.Fragment, null, children),
        LineChart: ({ children }: { children: React.ReactNode }) =>
            React.createElement(
                "div",
                { "data-testid": "line-chart" },
                children,
            ),
        Line: () => null,
        XAxis: () => null,
        YAxis: () => null,
        CartesianGrid: () => null,
        Tooltip: () => null,
        Legend: () => null,
    };
});

// ---------------------------------------------------------------------------
// GraficoLinhaTempo
// ---------------------------------------------------------------------------

const dadosExemplo: MonthPoint[] = [
    { mes: "Jan/26", Entradas: 1500, Gastos: 800 },
    { mes: "Fev/26", Entradas: 2000, Gastos: 1200 },
    { mes: "Mar/26", Entradas: 1800, Gastos: 900 },
];

describe("GraficoLinhaTempo", () => {
    it("renderiza o título 'Linha do Tempo — Últimos 3 Meses'", () => {
        render(<GraficoLinhaTempo data={dadosExemplo} />);
        expect(
            screen.getByText("Linha do Tempo — Últimos 3 Meses"),
        ).toBeInTheDocument();
    });

    it("renderiza o gráfico de linhas", () => {
        render(<GraficoLinhaTempo data={dadosExemplo} />);
        expect(screen.getByTestId("line-chart")).toBeInTheDocument();
    });

    it("renderiza sem erros com dados vazios", () => {
        expect(() => render(<GraficoLinhaTempo data={[]} />)).not.toThrow();
    });

    it("renderiza sem erros com valores zerados", () => {
        const dadosZerados: MonthPoint[] = [
            { mes: "Jan/26", Entradas: 0, Gastos: 0 },
        ];
        expect(() =>
            render(<GraficoLinhaTempo data={dadosZerados} />),
        ).not.toThrow();
    });

    it("renderiza sem erros com 3 meses de dados", () => {
        expect(() =>
            render(<GraficoLinhaTempo data={dadosExemplo} />),
        ).not.toThrow();
    });
});
