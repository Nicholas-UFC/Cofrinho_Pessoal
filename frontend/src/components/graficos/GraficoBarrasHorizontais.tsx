import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
} from "recharts";
import { formatarBRL } from "../../utils/format";
import { GraficoCard } from "../GraficoCard";
import type { CategoriaPoint } from "../../utils/graficos";

const AXIS_COLOR = "#94a3b8";

const tooltipStyle = {
    backgroundColor: "#0f172a",
    border: "1px solid #1e3a5f",
    color: "#f1f5f9",
};

interface Props {
    title: string;
    data: CategoriaPoint[];
    cor: string;
    mensagemVazia: string;
}

export function GraficoBarrasHorizontais({
    title,
    data,
    cor,
    mensagemVazia,
}: Props): React.JSX.Element {
    return (
        <GraficoCard title={title}>
            {data.length === 0 ? (
                <p
                    style={{ color: AXIS_COLOR }}
                    className="text-sm text-center py-8"
                >
                    {mensagemVazia}
                </p>
            ) : (
                <ResponsiveContainer width="100%" height={220}>
                    <BarChart data={data} layout="vertical">
                        <CartesianGrid
                            strokeDasharray="3 3"
                            stroke="#1e3a5f"
                        />
                        <XAxis
                            type="number"
                            stroke={AXIS_COLOR}
                            tick={{ fill: AXIS_COLOR }}
                            tickFormatter={(v: number) =>
                                `R$${v.toLocaleString("pt-BR")}`
                            }
                        />
                        <YAxis
                            type="category"
                            dataKey="nome"
                            stroke={AXIS_COLOR}
                            tick={{ fill: AXIS_COLOR }}
                            width={100}
                        />
                        <Tooltip
                            contentStyle={tooltipStyle}
                            formatter={(v: number) => formatarBRL(String(v))}
                        />
                        <Bar
                            dataKey="Total"
                            fill={cor}
                            radius={[0, 4, 4, 0]}
                        />
                    </BarChart>
                </ResponsiveContainer>
            )}
        </GraficoCard>
    );
}
