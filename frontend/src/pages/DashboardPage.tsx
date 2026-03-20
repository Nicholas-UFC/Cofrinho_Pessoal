import { useEffect, useState, type JSX } from "react";
import { getResumo, type Resumo } from "../api/financas";
import { formatBRL } from "../utils/format";

interface SummaryCard {
    label: string;
    value: string;
    icon: string;
    color: string;
}

export default function DashboardPage(): JSX.Element {
    const [resumo, setResumo] = useState<Resumo | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        getResumo()
            .then(({ data }) => {
                setResumo(data);
            })
            .catch(() => {
                setError("Erro ao carregar resumo financeiro.");
            })
            .finally(() => {
                setLoading(false);
            });
    }, []);

    if (loading) {
        return (
            <div className="flex items-center justify-center h-48">
                <p style={{ color: "#94a3b8" }}>Carregando...</p>
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

    const saldoColor = Number(resumo.saldo) >= 0 ? "#22c55e" : "#f87171";

    const cards: SummaryCard[] = [
        {
            label: "Total de Entradas",
            value: formatBRL(resumo.total_entradas),
            icon: "📈",
            color: "#22c55e",
        },
        {
            label: "Total de Gastos",
            value: formatBRL(resumo.total_gastos),
            icon: "📉",
            color: "#f87171",
        },
        {
            label: "Saldo",
            value: formatBRL(resumo.saldo),
            icon: "💰",
            color: saldoColor,
        },
    ];

    return (
        <div>
            <h1
                style={{ color: "#f1f5f9" }}
                className="text-2xl font-bold mb-6"
            >
                Dashboard
            </h1>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {cards.map((card) => (
                    <div
                        key={card.label}
                        style={{
                            backgroundColor: "#16213e",
                            border: "1px solid #1e3a5f",
                        }}
                        className="rounded-xl p-6 shadow"
                    >
                        <div className="flex items-center gap-3 mb-3">
                            <span className="text-2xl">{card.icon}</span>
                            <span
                                style={{ color: "#94a3b8" }}
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
        </div>
    );
}
