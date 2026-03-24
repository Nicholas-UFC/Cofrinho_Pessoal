import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
} from "recharts";
import { formatarBRL } from "../../utils/format";
import { GraficoCard } from "../GraficoCard";

const AXIS_COLOR = "#94a3b8";
const GREEN = "#22c55e";
const RED = "#f87171";

const tooltipStyle = {
    backgroundColor: "#0f172a",
    border: "1px solid #1e3a5f",
    color: "#f1f5f9",
};

interface Props {
    totalEntradas: number;
    totalGastos: number;
}

export function GraficoEntradasVsGastos({
    totalEntradas,
    totalGastos,
}: Props): React.JSX.Element {
    const data = [
        { name: "Resumo", Entradas: totalEntradas, Gastos: totalGastos },
    ];

    return (
        <GraficoCard title="Entradas vs Gastos">
            <ResponsiveContainer width="100%" height={220}>
                <BarChart data={data} barCategoryGap="40%">
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e3a5f" />
                    <XAxis
                        dataKey="name"
                        stroke={AXIS_COLOR}
                        tick={{ fill: AXIS_COLOR }}
                    />
                    <YAxis
                        stroke={AXIS_COLOR}
                        tick={{ fill: AXIS_COLOR }}
                        tickFormatter={(v: number) =>
                            `R$${v.toLocaleString("pt-BR")}`
                        }
                    />
                    <Tooltip
                        contentStyle={tooltipStyle}
                        formatter={(v: number) => formatarBRL(String(v))}
                    />
                    <Legend wrapperStyle={{ color: AXIS_COLOR }} />
                    <Bar
                        dataKey="Entradas"
                        fill={GREEN}
                        radius={[4, 4, 0, 0]}
                    />
                    <Bar dataKey="Gastos" fill={RED} radius={[4, 4, 0, 0]} />
                </BarChart>
            </ResponsiveContainer>
        </GraficoCard>
    );
}
