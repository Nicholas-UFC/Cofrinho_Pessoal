import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { GraficoBarrasHorizontais } from "../GraficoBarrasHorizontais";

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
// GraficoBarrasHorizontais
// ---------------------------------------------------------------------------

describe("GraficoBarrasHorizontais", () => {
    it("renderiza o título passado via prop", () => {
        render(
            <GraficoBarrasHorizontais
                title="Por Categoria"
                data={[]}
                cor="#f00"
                mensagemVazia="Sem dados"
            />,
        );
        expect(screen.getByText("Por Categoria")).toBeInTheDocument();
    });

    it("exibe mensagemVazia quando data está vazio", () => {
        render(
            <GraficoBarrasHorizontais
                title="Título"
                data={[]}
                cor="#f00"
                mensagemVazia="Nenhum gasto registrado"
            />,
        );
        expect(
            screen.getByText("Nenhum gasto registrado"),
        ).toBeInTheDocument();
    });

    it("não exibe mensagemVazia quando há dados", () => {
        const data = [{ nome: "Alimentação", Total: 150 }];
        render(
            <GraficoBarrasHorizontais
                title="Título"
                data={data}
                cor="#f00"
                mensagemVazia="Sem dados"
            />,
        );
        expect(screen.queryByText("Sem dados")).not.toBeInTheDocument();
    });

    it("renderiza o gráfico de barras quando há dados", () => {
        const data = [{ nome: "Alimentação", Total: 150 }];
        render(
            <GraficoBarrasHorizontais
                title="Título"
                data={data}
                cor="#f00"
                mensagemVazia="Sem dados"
            />,
        );
        expect(screen.getByTestId("bar-chart")).toBeInTheDocument();
    });

    it("não renderiza o gráfico quando data está vazio", () => {
        render(
            <GraficoBarrasHorizontais
                title="Título"
                data={[]}
                cor="#f00"
                mensagemVazia="Sem dados"
            />,
        );
        expect(screen.queryByTestId("bar-chart")).not.toBeInTheDocument();
    });

    it("renderiza sem erros com múltiplos itens de dados", () => {
        const data = [
            { nome: "Alimentação", Total: 150 },
            { nome: "Transporte", Total: 80 },
            { nome: "Lazer", Total: 200 },
        ];
        expect(() =>
            render(
                <GraficoBarrasHorizontais
                    title="Categorias"
                    data={data}
                    cor="#3b82f6"
                    mensagemVazia="Sem dados"
                />,
            ),
        ).not.toThrow();
    });
});
