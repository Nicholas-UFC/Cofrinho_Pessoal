import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
} from "recharts";
import { formatarBRL } from "../../utils/format";
import { GraficoCard } from "../GraficoCard";
import type { MonthPoint } from "../../utils/graficos";

const AXIS_COLOR = "#94a3b8";
const GREEN = "#22c55e";
const RED = "#f87171";

const tooltipStyle = {
    backgroundColor: "#0f172a",
    border: "1px solid #1e3a5f",
    color: "#f1f5f9",
};

interface Props {
    data: MonthPoint[];
}

export function GraficoLinhaTempo({ data }: Props): React.JSX.Element {
    return (
        <GraficoCard title="Linha do Tempo — Últimos 3 Meses">
            <ResponsiveContainer width="100%" height={220}>
                <LineChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e3a5f" />
                    <XAxis
                        dataKey="mes"
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
                    <Line
                        type="monotone"
                        dataKey="Entradas"
                        stroke={GREEN}
                        strokeWidth={2}
                        dot={{ r: 5, fill: GREEN }}
                        activeDot={{ r: 7 }}
                    />
                    <Line
                        type="monotone"
                        dataKey="Gastos"
                        stroke={RED}
                        strokeWidth={2}
                        dot={{ r: 5, fill: RED }}
                        strokeDasharray="5 5"
                        activeDot={{ r: 7 }}
                    />
                </LineChart>
            </ResponsiveContainer>
        </GraficoCard>
    );
}
