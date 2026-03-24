import { useEffect, useState, type JSX } from "react";
import {
    getResumo,
    getAllGastos,
    getAllEntradas,
    type Resumo,
    type Gasto,
    type Entrada,
} from "../api/financas";
import { formatarBRL } from "../utils/format";
import {
    buildLineData,
    buildCategoriaData,
    buildFonteData,
} from "../utils/graficos";
import { GraficoEntradasVsGastos } from "../components/graficos/GraficoEntradasVsGastos";
import { GraficoLinhaTempo } from "../components/graficos/GraficoLinhaTempo";
import { GraficoBarrasHorizontais } from "../components/graficos/GraficoBarrasHorizontais";

interface SummaryCard {
    label: string;
    value: string;
    icon: string;
    color: string;
}

const CARD_BG = "#16213e";
const CARD_BORDER = "1px solid #1e3a5f";
const AXIS_COLOR = "#94a3b8";
const GREEN = "#22c55e";
const RED = "#f87171";

export default function PaginaPainel(): JSX.Element {
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
            value: formatarBRL(resumo.total_entradas),
            icon: "📈",
            color: GREEN,
        },
        {
            label: "Total de Gastos",
            value: formatarBRL(resumo.total_gastos),
            icon: "📉",
            color: RED,
        },
        {
            label: "Saldo",
            value: formatarBRL(resumo.saldo),
            icon: "💰",
            color: saldoColor,
        },
    ];

    return (
        <div className="space-y-6">
            <h1 style={{ color: "#f1f5f9" }} className="text-2xl font-bold">
                Dashboard
            </h1>

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

            <GraficoEntradasVsGastos
                totalEntradas={Number(resumo.total_entradas)}
                totalGastos={Number(resumo.total_gastos)}
            />

            <GraficoLinhaTempo data={buildLineData(gastos, entradas)} />

            <GraficoBarrasHorizontais
                title="Gastos por Categoria"
                data={buildCategoriaData(gastos)}
                cor={RED}
                mensagemVazia="Nenhum gasto registrado."
            />

            <GraficoBarrasHorizontais
                title="Entradas por Fonte"
                data={buildFonteData(entradas)}
                cor={GREEN}
                mensagemVazia="Nenhuma entrada registrada."
            />
        </div>
    );
}
