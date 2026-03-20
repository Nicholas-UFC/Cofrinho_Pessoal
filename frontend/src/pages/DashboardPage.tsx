import { useEffect, useState, type JSX } from "react";
import {
    BarChart,
    Bar,
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
} from "recharts";
import {
    getResumo,
    getAllGastos,
    getAllEntradas,
    type Resumo,
    type Gasto,
    type Entrada,
} from "../api/financas";
import { formatBRL } from "../utils/format";

interface SummaryCard {
    label: string;
    value: string;
    icon: string;
    color: string;
}

interface MonthPoint {
    mes: string;
    Entradas: number;
    Gastos: number;
}

interface CategoriaPoint {
    nome: string;
    Total: number;
}

const CARD_BG = "#16213e";
const CARD_BORDER = "1px solid #1e3a5f";
const AXIS_COLOR = "#94a3b8";
const GREEN = "#22c55e";
const RED = "#f87171";

function labelMes(iso: string): string {
    const [year, month] = iso.split("-");
    const nomes = [
        "Jan",
        "Fev",
        "Mar",
        "Abr",
        "Mai",
        "Jun",
        "Jul",
        "Ago",
        "Set",
        "Out",
        "Nov",
        "Dez",
    ];
    return `${nomes[Number(month) - 1]}/${year.slice(2)}`;
}

function ultimos3Meses(): string[] {
    const meses: string[] = [];
    const now = new Date();
    for (let i = 2; i >= 0; i--) {
        const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
        const m = String(d.getMonth() + 1).padStart(2, "0");
        meses.push(`${String(d.getFullYear())}-${m}`);
    }
    return meses;
}

function buildLineData(gastos: Gasto[], entradas: Entrada[]): MonthPoint[] {
    const meses = ultimos3Meses();
    return meses.map((mes) => {
        const totalGastos = gastos
            .filter((g) => g.data.startsWith(mes))
            .reduce((acc, g) => acc + Number(g.valor), 0);
        const totalEntradas = entradas
            .filter((e) => e.data.startsWith(mes))
            .reduce((acc, e) => acc + Number(e.valor), 0);
        return {
            mes: labelMes(mes),
            Entradas: Number(totalEntradas.toFixed(2)),
            Gastos: Number(totalGastos.toFixed(2)),
        };
    });
}

function buildCategoriaData(gastos: Gasto[]): CategoriaPoint[] {
    const map = new Map<string, number>();
    gastos.forEach((g) => {
        const cat = g.categoria_nome ?? "Sem categoria";
        map.set(cat, (map.get(cat) ?? 0) + Number(g.valor));
    });
    return Array.from(map.entries())
        .map(([nome, total]) => ({ nome, Total: Number(total.toFixed(2)) }))
        .sort((a, b) => b.Total - a.Total);
}

function buildFonteData(entradas: Entrada[]): CategoriaPoint[] {
    const map = new Map<string, number>();
    entradas.forEach((e) => {
        const fonte = e.fonte_nome ?? "Sem fonte";
        map.set(fonte, (map.get(fonte) ?? 0) + Number(e.valor));
    });
    return Array.from(map.entries())
        .map(([nome, total]) => ({ nome, Total: Number(total.toFixed(2)) }))
        .sort((a, b) => b.Total - a.Total);
}

function ChartCard({
    title,
    children,
}: {
    title: string;
    children: React.ReactNode;
}): JSX.Element {
    return (
        <div
            style={{ backgroundColor: CARD_BG, border: CARD_BORDER }}
            className="rounded-xl p-6 shadow"
        >
            <h2
                style={{ color: "#f1f5f9" }}
                className="text-base font-semibold mb-4"
            >
                {title}
            </h2>
            {children}
        </div>
    );
}

const tooltipStyle = {
    backgroundColor: "#0f172a",
    border: "1px solid #1e3a5f",
    color: "#f1f5f9",
};

export default function DashboardPage(): JSX.Element {
    const [resumo, setResumo] = useState<Resumo | null>(null);
    const [gastos, setGastos] = useState<Gasto[]>([]);
    const [entradas, setEntradas] = useState<Entrada[]>([]);
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        Promise.all([getResumo(), getAllGastos(), getAllEntradas()])
            .then(([resumoRes, todosGastos, todasEntradas]) => {
                setResumo(resumoRes.data);
                setGastos(todosGastos);
                setEntradas(todasEntradas);
            })
            .catch(() => {
                setError("Erro ao carregar dados do dashboard.");
            })
            .finally(() => {
                setLoading(false);
            });
    }, []);

    if (loading) {
        return (
            <div className="flex items-center justify-center h-48">
                <p style={{ color: AXIS_COLOR }}>Carregando...</p>
            </div>
        );
    }

    if (error ?? !resumo) {
        return (
            <div className="flex items-center justify-center h-48">
                <p className="text-red-400">{error ?? "Sem dados."}</p>
            </div>
        );
    }

    const saldoColor = Number(resumo.saldo) >= 0 ? GREEN : RED;

    const cards: SummaryCard[] = [
        {
            label: "Total de Entradas",
            value: formatBRL(resumo.total_entradas),
            icon: "📈",
            color: GREEN,
        },
        {
            label: "Total de Gastos",
            value: formatBRL(resumo.total_gastos),
            icon: "📉",
            color: RED,
        },
        {
            label: "Saldo",
            value: formatBRL(resumo.saldo),
            icon: "💰",
            color: saldoColor,
        },
    ];

    const resumoBarData = [
        {
            name: "Resumo",
            Entradas: Number(resumo.total_entradas),
            Gastos: Number(resumo.total_gastos),
        },
    ];

    const lineData = buildLineData(gastos, entradas);
    const categoriaData = buildCategoriaData(gastos);
    const fonteData = buildFonteData(entradas);

    return (
        <div className="space-y-6">
            <h1 style={{ color: "#f1f5f9" }} className="text-2xl font-bold">
                Dashboard
            </h1>

            {/* Cards de resumo */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {cards.map((card) => (
                    <div
                        key={card.label}
                        style={{
                            backgroundColor: CARD_BG,
                            border: CARD_BORDER,
                        }}
                        className="rounded-xl p-6 shadow"
                    >
                        <div className="flex items-center gap-3 mb-3">
                            <span className="text-2xl">{card.icon}</span>
                            <span
                                style={{ color: AXIS_COLOR }}
                                className="text-sm font-medium"
                            >
                                {card.label}
                            </span>
                        </div>
                        <p
                            style={{ color: card.color }}
                            className="text-2xl font-bold"
                        >
                            {card.value}
                        </p>
                    </div>
                ))}
            </div>

            {/* Gráfico 1: Entradas vs Gastos (barra) */}
            <ChartCard title="Entradas vs Gastos">
                <ResponsiveContainer width="100%" height={220}>
                    <BarChart data={resumoBarData} barCategoryGap="40%">
                        <CartesianGrid
                            strokeDasharray="3 3"
                            stroke="#1e3a5f"
                        />
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
                            formatter={(v: number) => formatBRL(String(v))}
                        />
                        <Legend wrapperStyle={{ color: AXIS_COLOR }} />
                        <Bar
                            dataKey="Entradas"
                            fill={GREEN}
                            radius={[4, 4, 0, 0]}
                        />
                        <Bar
                            dataKey="Gastos"
                            fill={RED}
                            radius={[4, 4, 0, 0]}
                        />
                    </BarChart>
                </ResponsiveContainer>
            </ChartCard>

            {/* Gráfico 2: Linha do tempo — últimos 3 meses */}
            <ChartCard title="Linha do Tempo — Últimos 3 Meses">
                <ResponsiveContainer width="100%" height={220}>
                    <LineChart data={lineData}>
                        <CartesianGrid
                            strokeDasharray="3 3"
                            stroke="#1e3a5f"
                        />
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
                            formatter={(v: number) => formatBRL(String(v))}
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
            </ChartCard>

            {/* Gráfico 3: Gastos por categoria */}
            <ChartCard title="Gastos por Categoria">
                {categoriaData.length === 0 ? (
                    <p
                        style={{ color: AXIS_COLOR }}
                        className="text-sm text-center py-8"
                    >
                        Nenhum gasto registrado.
                    </p>
                ) : (
                    <ResponsiveContainer width="100%" height={220}>
                        <BarChart data={categoriaData} layout="vertical">
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
                                formatter={(v: number) => formatBRL(String(v))}
                            />
                            <Bar
                                dataKey="Total"
                                fill={RED}
                                radius={[0, 4, 4, 0]}
                            />
                        </BarChart>
                    </ResponsiveContainer>
                )}
            </ChartCard>

            {/* Gráfico 4: Entradas por fonte */}
            <ChartCard title="Entradas por Fonte">
                {fonteData.length === 0 ? (
                    <p
                        style={{ color: AXIS_COLOR }}
                        className="text-sm text-center py-8"
                    >
                        Nenhuma entrada registrada.
                    </p>
                ) : (
                    <ResponsiveContainer width="100%" height={220}>
                        <BarChart data={fonteData} layout="vertical">
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
                                formatter={(v: number) => formatBRL(String(v))}
                            />
                            <Bar
                                dataKey="Total"
                                fill={GREEN}
                                radius={[0, 4, 4, 0]}
                            />
                        </BarChart>
                    </ResponsiveContainer>
                )}
            </ChartCard>
        </div>
    );
}
